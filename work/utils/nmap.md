# nmap
*nmap is a network discovery and security auditing tool. It is used to scan networks for open ports, services, and vulnerabilities.*

## Installation
- Windows:
```sh
winget install nmap
```
- Linux (Debian/Ubuntu):
```sh
sudo apt install nmap
```
- Linux (Red Hat based):
```sh
sudo dnf install nmap
```
- macOS:
```sh
brew install nmap
```

## Basic usage (replace with your target IP or hostname)
```sh
nmap 192.168.1.1               # scan for open ports of common services
nmap -6 2001:db8::1            # scan IPv6 address
nmap device.domain.com         # scan by hostname, combine with -6 for IPv6
nmap 192.168.0.0/16            # scan an entire subnet (can take a very long time, better scan for specific ports to reduce time)
nmap ... -p 1024,1000-2000     # specify ports to scan
nmap ... -sV                   # detect service versions
nmap ... -O                    # detect operating system
nmap ... -A                    # aggressive scan (includes -sV and -O)
nmap ... -T4                   # faster scan (use with caution)
nmap ... --script vuln         # run vulnerability scripts
```

## Important notes
- Use nmap responsibly and ethically, especially when scanning networks that you do not own or manage.
