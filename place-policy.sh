#!/bin/sh
[ -f /etc/initrd-release ] || exit 0
mkdir -p /run/uki-xb /run/systemd
if mount -o ro -t vfat /dev/disk/by-uuid/ABCD-1234 /run/uki-xb; then
  cp /run/uki-xb/my-pcrlock.json /run/systemd/pcrlock-nopin.json || :
  umount /run/uki-xb
fi
[ -e /run/systemd/pcrlock-nopin.json ] || : > /run/systemd/pcrlock-nopin.json
udevadm settle --timeout=30 || true
exit 0