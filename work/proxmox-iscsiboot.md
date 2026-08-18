# Install Proxmox Virtual Environment on bare-metal host with iSCSI root disk.

## Preparation

- [ ] Have seperated NICs for iSCSI and network link, or use NPar function if NIC firmware supports it.
- [ ] Configured iSCSI boot parameters in host firmware (NIC ROM/UEFI); readable through iBFT
- [ ] Proxmox VE installation media (ISO, bootable USB, virtual CD/DVD, network boot, ...)
- [ ] ...

> [!WARNING]
> If you use the same NICs for both iSCSI-boot and network, you should let the iSCSI vlan become the PVID/native vlan of the trunk link to the host.
>
> `iscsistart` will got segfault when setting up network from iBFT with vlan tag.

## Boot into installer media

> [!NOTE]
> Boot into installer with debug mode (choose this option in installer's bootloader)
>
> This mode drop you into a shell before Proxmox install UI launched. From here you can connect to iSCSI storage, later Proxmox installer will properly detected it.
>
> In this mode, go to next steps with `Ctrl + D` key combination.

### Pre-install shell

Install iSCSI packages
```bash
cd /cdrom/debian/proxmox/packages/
dpkg -i libisns*.deb
dpkg -i libopeniscsiusr*.deb
dpkg -i open-iscsi*.deb
```

Set up network and connect to iSCSI LUN
```bash
modprobe iscsi_ibft
modprobe iscsi_tcp
iscsistart -f
iscsistart -N
iscsistart -b
```

Verify connection
```bash
ip a
lsblk
```

### Install Proxmox VE in the GUI

...

### After installation finished

Set-up chroot environment
```bash
mount /dev/pve/root /mnt
mount --bind /dev /mnt/dev
mount --bind /proc /mnt/proc
mount --bind /sys /mnt/sys
chroot /mnt /bin/bash
```

Chroot to installed disk
```bash
echo "ISCSI_AUTO=true" > /etc/iscsi/iscsi.initramfs
update-initramfs -u -k all
update-grub
```

## Finish iSCSI connection

### Setup multipath

```bash
apt update
apt install vim multipath-tools multipath-tools-boot
```

`/etc/multipath.conf`
```conf
defaults {
    user_friendly_names yes
    find_multipaths greedy

    polling_interval 5
    reassign_maps yes

    no_path_retry 20
    flush_on_last_del unused
    queue_without_daemon no

    failback immediate
    path_selector "service-time 0"

    dev_loss_tmo infinity
    fast_io_fail_tmo 5
}

blacklist {
    devnode "^(ram|raw|loop|fd|md|dm-|sr|scd|st|zd|zram|nbd)[0-9]*"

    # Only allow iSCSI-backed SCSI devices to be considered by multipath.
    protocol "!^scsi:iscsi$"
}
```

`/etc/lvm/lvm.conf` (append to existing file)
```conf
devices {
    multipath_component_detection = 1

    preferred_names = [
        "^/dev/mapper/",
        "^/dev/disk/by-id/dm-uuid-",
        "^/dev/disk/by-id/",
        "^/dev/sd"
    ]
}
```

`/etc/initramfs-tools/scripts/local-top/30-multipath-after-iscsi`
```bash
#!/bin/sh

PREREQ="iscsi"

prereqs() {
    echo "$PREREQ"
}

case "$1" in
prereqs)
    prereqs
    exit 0
    ;;
esac

/sbin/multipath
udevadm settle

exit 0
```

Shell:

```bash
chmod +x /etc/initramfs-tools/scripts/local-top/30-multipath-after-iscsi
update-initramfs -u -k all
reboot
```

### Connect to all other paths

```bash
echo InitiatorName=$(cat /sys/firmware/ibft/initiator/initiator-name) > /etc/iscsi/initiatorname.iscsi
```

After reboot, discover and connect all other targets to reach multipath capability.

```bash
iscsiadm -m discovery -t sendtargets -p <portal ip>:3260
iscsiadm -m node                                          # check discovered nodes
iscsiadm -m node --login                                  # login all discovered nodes
iscsiadm -m session                                       # check sessions
multipath -ll                                             # check multipath
iscsiadm -m node --op update -n node.startup -v automatic # reconnect after reboots
```

## Free up pve/data store

> [!TIP]
> Since we have shared volumes from SAN to store VM disk images, it's no need to keep the pve-data store.

Reclaim the space and extend root partition:

```bash
lvremove pve/data
lvextend -l +100%FREE /dev/pve/root
resize2fs /dev/pve/root
```

