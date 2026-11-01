LaCie Wireless Space - reference material (2026-11-01)

UM_WirelessSpace_EN.pdf (not included here: Seagate copyright; download it from the link below)
    Stock user manual (Seagate/LaCie,
    https://www.seagate.com/lacie-content/manual/UM_WirelessSpace_EN.pdf).
    Useful pages: 10 (1.4.1 Front View: WPS touch button, quick touch =
    WPS, long touch = Wi-Fi on/off), 11-12 (power button, reset),
    13 (1.8 Light Behavior: the LED table the OpenWrt build follows).
ws-wan-led-20261101.md
    WAN/LAN socket LED registers (PHY page 3 reg 16), state on 2026-11-01.

photos/
  board-top-overview.jpg            top of the board: 88E6161 switch, CPU,
                                    mini-PCIe Wi-Fi, USB cable connector at
                                    the right edge (red/white/green/black =
                                    USB, not the LED)
  microscope-J15-front-led-connector.jpg
                                    J15 = front LED connector (4 pins: VCC,
                                    R, G, B), C83 next to it, C314 + R334
                                    (100 ohm) below
  microscope-R108-C314-R334.jpg     area around J15 / R108 / R257
  front-edge-led-and-touch-pad.jpg  front edge with the replacement LEDs lit
                                    and the copper touch pad (WPS "sense
                                    cap", GPIO43) on the small board at left
  front-cover-inside.jpg            inside of the front cover: USB opening
                                    and light window; the touch pad sits
                                    behind the plain part of the cover

See ../NOTES.txt for the GPIO/latch details and the LED/button behaviour.
