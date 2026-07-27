# Install Docker CE on Debian-based Linux

This guide installs Docker Engine Community Edition from Docker's signed `apt`
repository. It covers supported releases of Debian and Ubuntu and is intended
for long-lived servers.

::: warning Production support
Use a release listed in Docker's current [Debian](https://docs.docker.com/engine/install/debian/#os-requirements)
or [Ubuntu](https://docs.docker.com/engine/install/ubuntu/#os-requirements)
requirements. Debian and Ubuntu derivatives, including Kali and Linux Mint,
are not officially supported even if a parent-distribution repository appears
to work.

Do not use the `get.docker.com` convenience script in production. It installs
the latest release with limited control over versions and dependencies.
:::

## Before installation

You need `sudo` access, outbound HTTPS access to `download.docker.com`, and a
supported CPU architecture. Confirm the operating system before selecting a
repository:

```sh
. /etc/os-release
printf 'Distribution: %s\nCodename: %s\n' "$PRETTY_NAME" "$VERSION_CODENAME"
dpkg --print-architecture
```

If this host already runs containers, inventory them and back up `/var/lib/docker`
and `/var/lib/containerd` before replacing packages. Removing conflicting
packages does not delete the data in those directories.

Remove distribution-provided Docker packages and standalone `containerd` or
`runc` packages that conflict with Docker CE:

```sh
sudo apt-get remove -y $(
  dpkg --get-selections \
    docker.io docker-compose docker-compose-v2 docker-doc docker-buildx \
    podman-docker containerd runc 2>/dev/null | cut -f1
)
```

It is safe if `apt-get` reports that none of these packages are installed.

## Add Docker's repository

Install the repository prerequisites:

```sh
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
```

Add the repository that matches the host. Do not use the Debian repository on
Ubuntu or the Ubuntu repository on Debian.

::: code-group

```sh [Debian]
sudo curl -fsSL https://download.docker.com/linux/debian/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
```

```sh [Ubuntu]
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
```

:::

Verify the downloaded key. Its fingerprint must be
`9DC8 5822 9FC7 DD38 854A E2D8 8D81 803C 0EBF CD88`:

```sh
gpg --show-keys --with-fingerprint /etc/apt/keyrings/docker.asc
sudo apt-get update
apt-cache policy docker-ce
```

The candidate package must come from `https://download.docker.com` and the
distribution codename shown earlier.

## Install Docker CE

List available stable versions:

```sh
apt-cache madison docker-ce
```

For a production fleet, test a version in staging and record its complete
version string in configuration management. Replace `<VERSION_STRING>` with an
exact value from the previous command:

```sh
VERSION_STRING='<VERSION_STRING>'

sudo apt-get install -y \
  docker-ce="$VERSION_STRING" \
  docker-ce-cli="$VERSION_STRING" \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin
```

For a newly provisioned host where the current stable release has already been
approved, install the repository's current candidate instead:

```sh
sudo apt-get install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin
```

Record all resolved package versions after installation:

```sh
dpkg-query -W \
  docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
```

## Configure the daemon

The default `json-file` logging driver can consume the host filesystem without
limit. The following baseline enables rotating local logs and keeps standalone
containers running during a compatible daemon outage.

If `/etc/docker/daemon.json` already exists, merge these settings into it rather
than overwriting the existing configuration.

```sh
sudo install -m 0755 -d /etc/docker
sudo tee /etc/docker/daemon.json >/dev/null <<'EOF'
{
  "live-restore": true,
  "log-driver": "local",
  "log-opts": {
    "max-size": "10m",
    "max-file": "5"
  }
}
EOF

sudo dockerd --validate --config-file=/etc/docker/daemon.json
sudo systemctl enable docker.service containerd.service
sudo systemctl restart docker.service
```

The logging defaults apply only to containers created after this change.
`live-restore` reduces downtime for daemon patch upgrades; it is not a
replacement for workload redundancy or a tested maintenance procedure.

## Verify the host

Check the services, client-to-daemon connection, storage driver, logging driver,
and a real container start:

```sh
sudo systemctl is-enabled docker.service containerd.service
sudo systemctl is-active docker.service containerd.service
sudo docker version
sudo docker info
sudo docker run --rm hello-world
sudo docker compose version
sudo docker buildx version
```

`overlay2` is the normal storage driver on supported Linux hosts. Investigate
any failed service before deploying workloads:

```sh
sudo journalctl -u docker.service --since today
```

## Secure production access

::: danger Docker access is root access
Membership in the `docker` group grants effective root access to the host. Keep
using `sudo`, or grant membership only to trusted administrators. Do not expose
the unauthenticated Docker API on TCP port `2375`; use an
[SSH Docker context](https://docs.docker.com/engine/security/protect-access/#use-ssh-to-protect-the-docker-daemon-socket)
or mutual TLS for remote administration.
:::

Docker creates packet-filtering rules for bridge networks. A published port can
bypass rules managed only through UFW, so do not assume that an UFW deny rule
protects it. In production:

- Publish only required ports and bind internal services to a specific address,
  such as `127.0.0.1:8080:8080`.
- Enforce ingress policy in the `DOCKER-USER` chain or in an upstream firewall.
- Do not set Docker's `iptables` or `ip6tables` options to `false`; doing so
  commonly breaks container networking.
- Keep the host kernel, Docker Engine, and container images patched, and monitor
  disk usage under `/var/lib/docker`.

See Docker's [firewall guidance](https://docs.docker.com/engine/network/packet-filtering-firewalls/)
before exposing any container port.

## Controlled upgrades

Test upgrades on a non-production host, back up state, and select the target
version explicitly:

```sh
sudo apt-get update
apt-cache madison docker-ce

VERSION_STRING='<TESTED_VERSION_STRING>'
sudo apt-get install -y \
  docker-ce="$VERSION_STRING" \
  docker-ce-cli="$VERSION_STRING" \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

sudo systemctl is-active docker.service containerd.service
sudo docker version
sudo docker ps
```

Do not leave Docker packages permanently held without a separate security patch
process. Review release notes and roll forward through normal package management
after validation.

## References

- [Install Docker Engine on Debian](https://docs.docker.com/engine/install/debian/)
- [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [Linux post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/)
- [Docker daemon security](https://docs.docker.com/engine/security/)
