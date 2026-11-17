#!/bin/sh
[ -f /etc/initrd-release ] || exit 0
mkdir -p /run/uki-xb /run/systemd
if mount -o ro -t vfat /dev/disk/by-uuid/@PART_UUID@ /run/uki-xb; then
  cp /run/uki-xb/@POLICY_FILE@ /run/systemd/pcrlock-nopin.json || :
  umount /run/uki-xb
fi
[ -e /run/systemd/pcrlock-nopin.json ] || : > /run/systemd/pcrlock-nopin.json
udevadm settle --timeout=30 || true
exit 0