# Install Docker CE on Red Hat-based Linux

This guide installs Docker Engine Community Edition from Docker's signed RPM
repository. It covers supported releases of Red Hat Enterprise Linux, CentOS
Stream, and Fedora and is intended for long-lived servers.

::: warning Production support
Use a release listed in Docker's current [RHEL](https://docs.docker.com/engine/install/rhel/#os-requirements),
[CentOS](https://docs.docker.com/engine/install/centos/#os-requirements), or
[Fedora](https://docs.docker.com/engine/install/fedora/#os-requirements)
requirements. RHEL-compatible derivatives such as Rocky Linux and AlmaLinux
are not officially covered by Docker's installation instructions. Validate
vendor support before using a parent-distribution repository in production.

Do not use the `get.docker.com` convenience script in production. It installs
the latest release with limited control over versions and dependencies.
:::

## Before installation

You need `sudo` access, outbound HTTPS access to `download.docker.com`, and a
supported CPU architecture. Confirm the host identity before selecting a
repository:

```sh
. /etc/os-release
printf 'Distribution: %s\nID: %s\nVersion: %s\n' \
  "$PRETTY_NAME" "$ID" "$VERSION_ID"
uname -m
```

If this host already runs containers, inventory them and back up `/var/lib/docker`
and `/var/lib/containerd` before replacing packages. Removing conflicting
packages does not delete the data in those directories.

Remove old or distribution-provided Docker packages:

```sh
sudo dnf remove -y \
  docker \
  docker-client \
  docker-client-latest \
  docker-common \
  docker-latest \
  docker-latest-logrotate \
  docker-logrotate \
  docker-selinux \
  docker-engine-selinux \
  docker-engine
```

On RHEL, Docker also requires the removal of the distribution's `podman` and
`runc` packages. Confirm that no existing Podman workload depends on them, then
run:

```sh
sudo dnf remove -y podman runc
```

It is safe if DNF reports that none of these packages are installed.

## Add Docker's repository

Use only the repository matching the host distribution.

::: code-group

```sh [RHEL]
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo \
  https://download.docker.com/linux/rhel/docker-ce.repo
```

```sh [CentOS Stream]
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo \
  https://download.docker.com/linux/centos/docker-ce.repo
```

```sh [Fedora]
sudo dnf config-manager addrepo --from-repofile \
  https://download.docker.com/linux/fedora/docker-ce.repo
```

:::

Confirm that only the stable Docker CE repository is enabled:

```sh
sudo dnf repolist --enabled | grep docker-ce-stable
sudo dnf makecache
```

When DNF first imports Docker's signing key, verify this complete fingerprint
before accepting it:

```text
060A 61C5 1B55 8A7F 742B 77AA C52F EB6B 621E 9F35
```

The repository files enable `gpgcheck=1`; do not disable package signature
verification to work around an installation error.

## Install Docker CE

List available stable versions:

```sh
dnf list docker-ce --showduplicates | sort -r
```

For a production fleet, test a version in staging and record its complete
version string in configuration management. Replace `<VERSION_STRING>` with an
exact value from the second column of the previous command:

```sh
VERSION_STRING='<VERSION_STRING>'

sudo dnf install -y \
  "docker-ce-$VERSION_STRING" \
  "docker-ce-cli-$VERSION_STRING" \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin
```

For a newly provisioned host where the current stable release has already been
approved, install the repository's current candidate instead:

```sh
sudo dnf install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin
```

Record all resolved package versions after installation:

```sh
rpm -q \
  docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
```

## Configure the daemon

Docker is installed but not started automatically on RPM-based distributions.
Configure it before the first start. The default `json-file` logging driver can
consume the host filesystem without limit; this baseline enables rotating local
logs and keeps standalone containers running during a compatible daemon outage.

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
sudo systemctl enable --now docker.service containerd.service
```

The logging defaults apply only to containers created after this change.
`live-restore` reduces downtime for daemon patch upgrades; it is not a
replacement for workload redundancy or a tested maintenance procedure.

Keep SELinux in enforcing mode. Docker's packages install the required policy;
disabling SELinux hides policy problems and weakens host isolation.

```sh
getenforce
```

## Verify the host

Check the services, client-to-daemon connection, storage driver, security
options, logging driver, and a real container start:

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

On Fedora, if the journal reports `failed to find iptables`, select the nftables
implementation and restart Docker:

```sh
sudo alternatives --set iptables /usr/bin/iptables-nft
sudo systemctl restart docker.service
```

## Secure production access

::: danger Docker access is root access
Membership in the `docker` group grants effective root access to the host. Keep
using `sudo`, or grant membership only to trusted administrators. Do not expose
the unauthenticated Docker API on TCP port `2375`; use an
[SSH Docker context](https://docs.docker.com/engine/security/protect-access/#use-ssh-to-protect-the-docker-daemon-socket)
or mutual TLS for remote administration.
:::

Docker creates its own packet-filtering rules and integrates bridge interfaces
with firewalld. Do not assume that a firewalld zone blocks a port published by
Docker. In production:

- Publish only required ports and bind internal services to a specific address,
  such as `127.0.0.1:8080:8080`.
- Enforce ingress policy in the `DOCKER-USER` chain or in an upstream firewall.
- Do not set Docker's `iptables` or `ip6tables` options to `false`; doing so
  commonly breaks container networking.
- Keep SELinux enforcing and do not run containers with `--privileged` merely
  to bypass a policy or permissions error.
- Keep the host kernel, Docker Engine, and container images patched, and monitor
  disk usage under `/var/lib/docker`.

See Docker's [firewall guidance](https://docs.docker.com/engine/network/packet-filtering-firewalls/)
before exposing any container port.

## Controlled upgrades

Test upgrades on a non-production host, back up state, and select the target
version explicitly:

```sh
sudo dnf makecache
dnf list docker-ce --showduplicates | sort -r

VERSION_STRING='<TESTED_VERSION_STRING>'
sudo dnf install -y \
  "docker-ce-$VERSION_STRING" \
  "docker-ce-cli-$VERSION_STRING" \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

sudo systemctl is-active docker.service containerd.service
sudo docker version
sudo docker ps
```

Do not exclude Docker packages from updates indefinitely without a separate
security patch process. Review release notes and roll forward through normal
package management after validation.

## References

- [Install Docker Engine on RHEL](https://docs.docker.com/engine/install/rhel/)
- [Install Docker Engine on CentOS](https://docs.docker.com/engine/install/centos/)
- [Install Docker Engine on Fedora](https://docs.docker.com/engine/install/fedora/)
- [Linux post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/)
- [Docker daemon security](https://docs.docker.com/engine/security/)
