"""SQMeter main board v1 - netlist-level design description.

Each part: ref, lib_id, value, footprint, lcsc, pins {pin_number: net}.
Net None = no-connect. Power nets are drawn with power symbols.

SQM_VARIANT selects the MCU block:
  module - ESP32-S3-WROOM-1 soldered down, native USB-C (JLC assembled)
  devkit - ESP32-S3-DevKitC-1 (N16R8) plugged into 2x22 sockets
  zero   - Waveshare ESP32-S3-Zero-M (pre-soldered headers) plugged into 2x9 sockets
The plug-in variants feed the board's 5V into the dev board's 5V pin through a Schottky and take
3V3 back from the dev board's LDO for the sensors. All variants share GPIO_MAP, so one firmware
pin default fits every board.
"""
import os

VARIANT = os.environ.get('SQM_VARIANT', 'module')
assert VARIANT in ('module', 'devkit', 'zero'), VARIANT
DEVKIT = VARIANT == 'devkit'
ZERO = VARIANT == 'zero'
PLUGIN = DEVKIT or ZERO      # MCU is an off-the-shelf board on sockets
NAME = 'SQMeter-Hardware' + {'module': '', 'devkit': '-DevKit', 'zero': '-Zero'}[VARIANT]

# One GPIO map for every variant. Limited by the ESP32-S3-Zero, whose 2.54 mm headers only carry
# GPIO1-13 (+43/44 console): GPIO3 is a strapping pin, so 1,2,4-13 are the twelve usable pins.
GPIO_MAP = {
    1: 'RG_TX', 2: 'RG_RX',          # UART to RG-15
    4: 'WIND_DIR', 5: 'WIND_SPD',    # vane must be ADC1 (GPIO1-10)
    6: 'AUX1', 7: 'AUX2',
    10: 'SDA2', 11: 'SCL2',          # second I2C bus: a second TSL2591 (both are fixed at 0x29)
    8: 'SDA', 9: 'SCL',
    12: 'GPS_TX', 13: 'GPS_RX',      # UART to GPS
}

POWER_NETS = {'GND': 'power:GND', '+3V3': 'power:+3V3', '+12V': 'power:+12V', 'VBUS': 'power:VBUS', '+5V': 'power:+5V'}

FP = dict(
    R='Resistor_SMD:R_0603_1608Metric',
    C='Capacitor_SMD:C_0603_1608Metric',
    C0805='Capacitor_SMD:C_0805_2012Metric',
)

parts = []
blocks = []  # (title, [refs]) for schematic layout


def P(ref, lib, value, fp, pins, lcsc='', desc=''):
    parts.append(dict(ref=ref, lib=lib, value=value, fp=fp, pins=pins, lcsc=lcsc, desc=desc))
    return ref


def R(ref, value, a, b, lcsc=''):
    return P(ref, 'Device:R', value, FP['R'], {'1': a, '2': b}, lcsc)


def C(ref, value, a, b, lcsc='', fp=FP['C']):
    return P(ref, 'Device:C', value, fp, {'1': a, '2': b}, lcsc)


# ── Power input ───────────────────────────────────────────────────────────────
RAIL = '+5V' if PLUGIN else '+3V3'  # buck output
blocks.append(('12 V input, protection, ' + ('5V buck to dev board' if PLUGIN else '3V3 buck'), [
    P('J1', 'Connector_Generic:Conn_01x02', '12V IN', 'Connector_Phoenix_MSTB:PhoenixContact_MSTBA_2,5_2-G-5,08_1x02_P5.08mm_Horizontal',
      {'1': 'VIN_RAW', '2': 'GND'}, 'C3697', 'Pluggable 5.08 mm (2EDGRC): 1 = +12 V, 2 = GND'),
    P('F1', 'Device:Polyfuse', '1.5A 24V', 'Fuse:Fuse_1812_4532Metric', {'1': 'VIN_RAW', '2': 'VIN_F'}, 'C32404', 'SMD1812P150TF/24'),
    P('D1', 'Device:D_TVS', 'SMBJ18CA', 'Diode_SMD:D_SMB', {'1': 'VIN_F', '2': 'GND'}, 'C78413', 'Bidirectional TVS'),
    P('Q1', 'Transistor_FET:AO3401A', 'AO3401A', 'Package_TO_SOT_SMD:SOT-23', {'1': 'Q1_G', '2': '+12V', '3': 'VIN_F'}, 'C15127',
      'Reverse-polarity protection'),
    R('R19', '10k', '+12V', 'Q1_G', 'C25804'),  # R19/R1 divider: Vgs = -Vin/2, inside the FET's 12 V limit up to 24 V in
    R('R1', '10k', 'Q1_G', 'GND', 'C25804'),
    (P('D3', 'Device:D_Schottky', 'SS34', 'Diode_SMD:D_SMA', {'1': 'DK_5V', '2': '+5V'}, 'C8678',
       'Dev board USB can\'t back-feed the buck; buck can\'t push into a PC') if PLUGIN else
     P('D3', 'Device:D_Schottky', 'SS34', 'Diode_SMD:D_SMA', {'1': '+12V', '2': 'VBUS'}, 'C8678', 'USB power OR')),
    P('C1', 'Device:C_Polarized', '100u 35V', 'Capacitor_SMD:CP_Elec_8x10', {'1': '+12V', '2': 'GND'}, 'C165636', 'BXJ 105C low-ESR'),
    C('C2', '10u 25V', '+12V', 'GND', 'C15850', FP['C0805']),
    C('C3', '10u 25V', '+12V', 'GND', 'C15850', FP['C0805']),
    (P('U1', 'Regulator_Switching:AP63205WU', 'AP63205WU', 'Package_TO_SOT_SMD:TSOT-23-6',
       {'1': '+5V', '2': '+12V', '3': '+12V', '4': 'GND', '5': 'SW', '6': 'BST'}, 'C2071056') if PLUGIN else
     P('U1', 'Regulator_Switching:AP63203WU', 'AP63203WU', 'Package_TO_SOT_SMD:TSOT-23-6',
       {'1': '+3V3', '2': '+12V', '3': '+12V', '4': 'GND', '5': 'SW', '6': 'BST'}, 'C780769')),
    C('C4', '100n', 'BST', 'SW', 'C14663'),
    P('L1', 'Device:L', '6.8u 3A' if PLUGIN else '4.7u 3.3A', 'Inductor_SMD:L_Sunlord_SWPA6045S', {'1': 'SW', '2': RAIL},
      'C57254' if PLUGIN else 'C78804', 'Sunlord SWPA6045S'),
    C('C5', '22u', RAIL, 'GND', 'C45783', FP['C0805']),
    C('C6', '22u', RAIL, 'GND', 'C45783', FP['C0805']),
    P('F2', 'Device:Polyfuse', '0.5A 24V', 'Fuse:Fuse_1206_3216Metric', {'1': '+12V', '2': 'RG_PWR'}, 'C492011', 'RG-15 supply, SMD1206P050TF/24'),
]))

def by_gpio(names, fixed):
    """Header/module pin -> net, from a {pin: label} table where GPIO labels are ints."""
    out = {}
    for pin, label in names.items():
        out[str(pin)] = fixed.get(label, GPIO_MAP.get(label)) if not isinstance(label, int) else GPIO_MAP.get(label)
    return out


if VARIANT == 'module':
    # ── USB-C ─────────────────────────────────────────────────────────────────────
    blocks.append(('USB-C (native USB, power + flashing)', [
        P('J2', 'Connector:USB_C_Receptacle_USB2.0_16P', 'USB-C', 'Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12',
          {'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'A4': 'VBUS', 'A9': 'VBUS', 'B4': 'VBUS', 'B9': 'VBUS',
           'A5': 'CC1', 'B5': 'CC2', 'A6': 'USB_DP', 'B6': 'USB_DP', 'A7': 'USB_DN', 'B7': 'USB_DN',
           'A8': None, 'B8': None, 'SH': 'GND'}, 'C165948'),
        R('R2', '5.1k', 'CC1', 'GND', 'C23186'),
        R('R3', '5.1k', 'CC2', 'GND', 'C23186'),
        P('U2', 'Power_Protection:USBLC6-2SC6', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6',
          {'1': 'USB_DP', '6': 'USB_DP', '3': 'USB_DN', '4': 'USB_DN', '2': 'GND', '5': 'VBUS'}, 'C7519'),
    ]))

    # ── ESP32-S3 module ──────────────────────────────────────────────────────────
    from libs import pins as _sym_pins
    esp = {}
    for p in _sym_pins('RF_Module:ESP32-S3-WROOM-1'):
        nm = p['name']
        esp[p['num']] = GPIO_MAP.get(int(nm[2:])) if nm.startswith('IO') and nm[2:].isdigit() else None
    esp.update({'1': 'GND', '40': 'GND', '41': 'GND', '2': '+3V3', '3': 'EN', '27': 'BOOT',
                '13': 'USB_DN', '14': 'USB_DP', '24': 'LED', '36': 'U0RXD', '37': 'U0TXD'})  # 24 = IO47
    blocks.append(('ESP32-S3', [
        P('U3', 'RF_Module:ESP32-S3-WROOM-1', 'ESP32-S3-WROOM-1-N16R8', 'RF_Module:ESP32-S3-WROOM-1', esp, 'C2913202'),
        C('C7', '10u', '+3V3', 'GND', 'C15850', FP['C0805']),
        C('C8', '100n', '+3V3', 'GND', 'C14663'),
        R('R4', '10k', '+3V3', 'EN', 'C25804'),
        C('C9', '1u', 'EN', 'GND', 'C15849'),
        P('SW1', 'Switch:SW_Push', 'RESET', 'Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A', {'1': 'EN', '2': 'GND'}, 'C318884'),
        R('R5', '10k', '+3V3', 'BOOT', 'C25804'),
        P('SW2', 'Switch:SW_Push', 'BOOT', 'Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A', {'1': 'BOOT', '2': 'GND'}, 'C318884'),
        R('R6', '1k', 'LED', 'LED_A', 'C21190'),
        P('D4', 'Device:LED', 'STATUS', 'LED_SMD:LED_0603_1608Metric', {'1': 'GND', '2': 'LED_A'}, 'C12624'),
        P('TP1', 'Connector:TestPoint', 'U0RXD', 'TestPoint:TestPoint_Pad_D1.5mm', {'1': 'U0RXD'}),
        P('TP2', 'Connector:TestPoint', 'U0TXD', 'TestPoint:TestPoint_Pad_D1.5mm', {'1': 'U0TXD'}),
        P('TP3', 'Connector:TestPoint', 'GND', 'TestPoint:TestPoint_Pad_D1.5mm', {'1': 'GND'}),
        P('TP4', 'Connector:TestPoint', '3V3', 'TestPoint:TestPoint_Pad_D1.5mm', {'1': '+3V3'}),
    ]))

elif DEVKIT:
    # ── ESP32-S3-DevKitC-1 on sockets ───────────────────────────────────────
    # Header pinout per Espressif user guide v1.1 (J1 left, J3 right, pin 1 at the antenna end).
    PWR = {'3V3': '+3V3', '5V': 'DK_5V', 'G': 'GND', 'RST': None, 'TX': None, 'RX': None}
    j1 = ['3V3', '3V3', 'RST', 4, 5, 6, 7, 15, 16, 17, 18, 8, 3, 46, 9, 10, 11, 12, 13, 14, '5V', 'G']
    j3 = ['G', 'TX', 'RX', 1, 2, 42, 41, 40, 39, 38, 37, 36, 35, 0, 45, 48, 47, 21, 20, 19, 'G', 'G']
    dk1 = by_gpio(dict(enumerate(j1, 1)), PWR)
    dk3 = by_gpio(dict(enumerate(j3, 1)), PWR)
    dk3['1'] = None  # G under the antenna keepout; the DevKit ties all its G pins together
    SOCK = 'Connector_PinSocket_2.54mm:PinSocket_1x22_P2.54mm_Vertical'
    blocks.append(('ESP32-S3-DevKitC-1 sockets', [
        P('J11', 'Connector_Generic:Conn_01x22', 'DevKitC-1 J1', SOCK, dk1, 'C41376161',
          'Female 1x22 socket for DevKitC-1 header J1 (3V3 ... 5V, G)'),
        P('J12', 'Connector_Generic:Conn_01x22', 'DevKitC-1 J3', SOCK, dk3, 'C41376161',
          'Female 1x22 socket for DevKitC-1 header J3 (G, TX, RX ... G, G)'),
    ]))

else:
    # ── Waveshare ESP32-S3-Zero-M on sockets ────────────────────────────────
    # Waveshare pinout (top view, USB-C at the top): left column 5V, GND, 3V3, GP1-GP6;
    # right column TX(43), RX(44), GP13 ... GP7. Rows 15.24 mm apart, 2.54 mm pitch.
    PWR = {'3V3': '+3V3', '5V': 'DK_5V', 'G': 'GND', 'TX': None, 'RX': None}
    left = ['5V', 'G', '3V3', 1, 2, 3, 4, 5, 6]
    right = ['TX', 'RX', 13, 12, 11, 10, 9, 8, 7]
    SOCK = 'Connector_PinSocket_2.54mm:PinSocket_1x09_P2.54mm_Vertical'
    blocks.append(('Waveshare ESP32-S3-Zero-M sockets', [
        P('J11', 'Connector_Generic:Conn_01x09', 'Zero left', SOCK, by_gpio(dict(enumerate(left, 1)), PWR), 'C22438159',
          'Female 1x9 socket: Zero left column (5V, GND, 3V3, GP1-GP6), pin 1 at the USB end'),
        P('J12', 'Connector_Generic:Conn_01x09', 'Zero right', SOCK, by_gpio(dict(enumerate(right, 1)), PWR), 'C22438159',
          'Female 1x9 socket: Zero right column (TX, RX, GP13-GP7), pin 1 at the USB end'),
    ]))

# ── I2C sensor ports ──────────────────────────────────────────────────────────
XH4 = 'Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical'
i2c = [P(f'J{n}', 'Connector_Generic:Conn_01x04', name, XH4, {'1': 'GND', '2': '+3V3', '3': 'SDA', '4': 'SCL'}, 'C144395',
         'JST-XH: 1 GND, 2 3V3, 3 SDA, 4 SCL')
       for n, name in ((3, 'I2C TSL2591 #1'), (4, 'I2C MLX90614'), (5, 'I2C BME280'), (6, 'I2C SPARE'))]
blocks.append(('I2C sensor ports (identical pinout)', i2c + [
    P('J13', 'Connector_Generic:Conn_01x04', 'I2C-2 TSL2591 #2', XH4, {'1': 'GND', '2': '+3V3', '3': 'SDA2', '4': 'SCL2'}, 'C144395',
      'JST-XH, second I2C bus (GPIO10/11): 1 GND, 2 3V3, 3 SDA, 4 SCL'),
    R('R20', '4.7k', '+3V3', 'SDA2', 'C23162'),
    R('R21', '4.7k', '+3V3', 'SCL2', 'C23162'),
    P('U7', 'Power_Protection:USBLC6-2SC6', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6',
      {'1': 'SDA2', '6': 'SDA2', '3': 'SCL2', '4': 'SCL2', '2': 'GND', '5': '+3V3'}, 'C7519', 'I2C-2 ESD'),
    R('R7', '4.7k', '+3V3', 'SDA', 'C23162'),
    R('R8', '4.7k', '+3V3', 'SCL', 'C23162'),
    P('U4', 'Power_Protection:USBLC6-2SC6', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6',
      {'1': 'SDA', '6': 'SDA', '3': 'SCL', '4': 'SCL', '2': 'GND', '5': '+3V3'}, 'C7519', 'I2C ESD'),
]))

# ── GPS ───────────────────────────────────────────────────────────────────────
blocks.append(('GPS (UART1)', [
    P('J7', 'Connector_Generic:Conn_01x04', 'GPS', XH4, {'1': 'GND', '2': '+3V3', '3': 'GPS_TXO', '4': 'GPS_RXI'}, 'C144395',
      'JST-XH: 1 GND, 2 3V3, 3 GPS TX (to ESP RX), 4 GPS RX'),
    R('R9', '100', 'GPS_TXO', 'GPS_RX', 'C22775'),
    R('R10', '100', 'GPS_TX', 'GPS_RXI', 'C22775'),
]))

# ── RG-15 ─────────────────────────────────────────────────────────────────────
blocks.append(('RG-15 rain sensor (UART2)', [
    P('J8', 'Connector_Generic:Conn_01x04', 'RG-15', 'Connector_Phoenix_MC:PhoenixContact_MC_1,5_4-G-3.5_1x04_P3.50mm_Horizontal',
      {'1': 'GND', '2': 'RG_PWR', '3': 'RG_TXO', '4': 'RG_RXI'}, 'C5188297', 'Pluggable 3.5 mm (15EDGRC): 1 GND, 2 V+ (12 V), 3 RG TX, 4 RG RX'),
    R('R11', '100', 'RG_TXO', 'RG_RX', 'C22775'),
    R('R12', '100', 'RG_TX', 'RG_RXI', 'C22775'),
    P('U5', 'Power_Protection:USBLC6-2SC6', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6',
      {'1': 'RG_TXO', '6': 'RG_TXO', '3': 'RG_RXI', '4': 'RG_RXI', '2': 'GND', '5': '+3V3'}, 'C7519', 'RG-15 ESD'),
]))

# ── Wind ──────────────────────────────────────────────────────────────────────
blocks.append(('Wind: anemometer + vane', [
    P('J9', 'Connector_Generic:Conn_01x05', 'WIND', 'Connector_Phoenix_MC:PhoenixContact_MC_1,5_5-G-3.5_1x05_P3.50mm_Horizontal',
      {'1': 'WSPD_EXT', '2': 'GND', '3': 'WDIR_EXT', '4': 'GND', '5': '+3V3'}, 'C5188298',
      'Pluggable 3.5 mm (15EDGRC): 1 SPD, 2 GND, 3 DIR, 4 GND, 5 3V3 (pot vane excitation)'),
    R('R13', '10k', '+3V3', 'WSPD_EXT', 'C25804'),
    R('R14', '1k', 'WSPD_EXT', 'WIND_SPD', 'C21190'),
    C('C10', '100n', 'WIND_SPD', 'GND', 'C14663'),
    P('JP1', 'Jumper:SolderJumper_2_Bridged', 'VANE PU', 'Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm',
      {'1': '+3V3', '2': 'VANE_PU'}, desc='Cut for potentiometer vanes (Davis 6410)'),
    R('R15', '10k', 'VANE_PU', 'WDIR_EXT', 'C25804'),
    R('R16', '1k', 'WDIR_EXT', 'WIND_DIR', 'C21190'),
    C('C11', '100n', 'WIND_DIR', 'GND', 'C14663'),
    P('U6', 'Power_Protection:USBLC6-2SC6', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6',
      {'1': 'WSPD_EXT', '6': 'WSPD_EXT', '3': 'WDIR_EXT', '4': 'WDIR_EXT', '2': 'GND', '5': '+3V3'}, 'C7519', 'Wind ESD'),
]))

# ── Aux + mechanical ──────────────────────────────────────────────────────────
blocks.append(('Aux GPIO + mounting', [
    P('J10', 'Connector_Generic:Conn_01x04', 'AUX', XH4,
      {'1': 'GND', '2': '+3V3', '3': 'AUX1', '4': 'AUX2'}, 'C144395',
      'JST-XH: 1 GND, 2 3V3, 3 IO6, 4 IO7'),
] + [P(f'H{n}', 'Mechanical:MountingHole', 'M3', 'MountingHole:MountingHole_3.2mm_M3', {}) for n in range(1, 5)]))

FLAGS = ['GND', '+12V', '+3V3', '+5V'] if PLUGIN else ['GND', '+12V', '+3V3', 'VBUS']
