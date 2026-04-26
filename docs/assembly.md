# Assembly Guide

TODO: This guide will be completed once the hardware design is finalised.

## Tools required

TODO: list tools once BOM is settled.

- Soldering iron with fine tip
- Solder (leaded or lead-free)
- Flux
- IPA for cleaning
- Multimeter
- TODO: add any specialised tools

## Component placement reference

Use the InteractiveHtmlBom at `hardware/ibom/ibom.html` for component placement. Open in any browser — no server required.

## Soldering order

TODO: define order based on final component selection.

General guidance:
1. SMD passives (resistors, capacitors) before larger components
2. ICs before connectors
3. Through-hole connectors last

## Sensor headers and connectors

TODO: document I2C sensor header pinout, UART connector pinout, and GPS module interface.

## ESP32 module

TODO: document ESP32 module type, footprint, and mounting.

## Power supply

TODO: document power input, voltage regulator, decoupling requirements.

## Enclosure fitment

3D printed enclosure files will be hosted on Printables (TODO: add link). This section will describe how the PCB mounts inside the enclosure, connector cutout locations, and any fitment notes.

## Testing and bring-up

TODO: outline bring-up sequence.

1. Visual inspection — check for solder bridges, missing components
2. Power-on test — verify 3.3V rail before connecting sensors
3. Firmware flash — see [SQMeter firmware repo](https://github.com/DeanJ87/SQMeter)
4. Sensor check — verify I2C scan returns expected addresses
5. Web UI — connect to device AP, verify sensor readings
