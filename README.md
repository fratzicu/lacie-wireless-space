# LaCie Wireless Space: OpenWrt 25.12 + mainline U-Boot

Modern firmware for the LaCie Wireless Space (Neil Poulton design, board
ASTON_WS_GN3): a NAS with a 3.5" disk, a 4-port switch and Wi-Fi.

- **OpenWrt 25.12.6** (kernel 6.12) with the switch (DSA), Wi-Fi, disk, fan
  control, SMB sharing (ksmbd) and the front light and touch button working
  as described in the stock manual
- **U-Boot 2026.10** port with a boot menu, web recovery and flashing from
  TFTP, HTTP or USB

| | |
|---|---|
| SoC | Marvell Kirkwood 88F6281 A1 |
| RAM / flash | 256 MiB DDR2 / 128 MiB NAND |
| Switch | Marvell 88E6161 (lan1-3, wan) |
| Wi-Fi | Ralink RT3092 mini-PCIe (rt2800pci) |
| Disk | internal SATA, front USB 2.0 |

## Source

- OpenWrt: [fratzicu/openwrt-upstream, branch `lacie-wireless-space`](https://github.com/fratzicu/openwrt-upstream/tree/lacie-wireless-space)
  (on top of v25.12.6; also adds the LaCie Internet Space, Orion 88F5182)
- U-Boot: [fratzicu/u-boot, branch `wireless-space`](https://github.com/fratzicu/u-boot/tree/wireless-space)
- `patches/`: the same changes as plain diffs

Build OpenWrt with target kirkwood/generic, device `lacie_wireless-space`
(`openwrt-config-excerpt.txt`). Build U-Boot with
`make wireless_space_defconfig && make CROSS_COMPILE=arm-...-`.

## Images

The built images are attached to the
[Releases](https://github.com/fratzicu/lacie-wireless-space/releases).
**Installing them replaces the LaCie firmware and boot loader.** Moving a
stock box over needs the serial console and UART boot (kwboot); read
`NOTES.txt` and `FLASHING.txt` first and make a full NAND backup.

## Front light and touch button

Following the light table in the stock manual (1.8 Light Behavior):

| Light | Meaning |
|---|---|
| blue, fast then slower blinking | booting |
| blue steady | ready, Wi-Fi on |
| green steady | ready, Wi-Fi off |
| other colour flickers | disk access |
| blue/green fast blinking | front touch area held |
| blue/green slow blinking | WPS pairing (2 min) |
| red steady | no disk, shutting down |
| red blinking | failsafe / ready for factory reset |
| blue/green/red blinking | firmware upgrade |

Front touch area: short touch = WPS push button, held 3 s = Wi-Fi on/off.
The light is one RGB LED behind a latch clocked by MPP42, driven with the
kernel `gpio-latch` driver. Details in `NOTES.txt`.

## Files

- `NOTES.txt`: hardware findings, GPIO map, PHY LED registers, fan, build
- `FLASHING.txt`: sysupgrade, boot menu, web recovery, TFTP, HTTP, USB,
  kwboot, back to stock
- `docs/`: board photos and notes. The stock user manual is at
  <https://www.seagate.com/lacie-content/manual/UM_WirelessSpace_EN.pdf>
- `tools/kwrs.py`: Marvell BootROM 4-bit Reed-Solomon ECC encoder/checker
  (block 0 must carry it); `tools/ysend.py`: YMODEM sender for U-Boot `loady`

Not included on purpose: stock LaCie NAND dumps (LaCie's firmware) and
configuration backups.
