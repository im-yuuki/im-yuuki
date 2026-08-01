# iperf3
*iperf3 is a tool for active measurements of the maximum achievable bandwidth on IP networks.*

## Installation
- Windows:
```sh
winget install iperf3
```
- Linux (Debian/Ubuntu):
```sh
sudo apt install iperf3
```
- Linux (Red Hat based):
```sh
sudo dnf install iperf3
```
- macOS:
```sh
brew install iperf3
```

## Basic usage

### Server mode
By default, iperf3 listens on port 5201, both TCP and UDP.
```sh
iperf3 -s   # run --help for more options, e.g. to specify port or protocol
```

### Client mode 
Replace `<server_ip>` with the IP address of the iperf3 server.
```sh
iperf3 -c <server_ip>