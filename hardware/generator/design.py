"""SQMeter main board v1 - netlist-level design description.

Each part: ref, lib_id, value, footprint, lcsc, pins {pin_number: net}.
Net None = no-connect. Power nets are drawn with power symbols.
"""

POWER_NETS = {'GND': 'power:GND', '+3V3': 'power:+3V3', '+12V': 'power:+12V', 'VBUS': 'power:VBUS'}

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
blocks.append(('12 V input, protection, 3V3 buck', [
    P('J1', 'Connector_Generic:Conn_01x02', '12V IN', 'Connector_Phoenix_MSTB:PhoenixContact_MSTBA_2,5_2-G-5,08_1x02_P5.08mm_Horizontal',
      {'1': 'VIN_RAW', '2': 'GND'}, desc='Pluggable 5.08 mm: 1 = +12 V, 2 = GND'),
    P('F1', 'Device:Polyfuse', '1.5A', 'Fuse:Fuse_1812_4532Metric', {'1': 'VIN_RAW', '2': 'VIN_F'}),
    P('D1', 'Device:D_TVS', 'SMBJ18CA', 'Diode_SMD:D_SMB', {'1': 'VIN_F', '2': 'GND'}, desc='Bidirectional TVS'),
    P('Q1', 'Transistor_FET:AO3401A', 'AO3401A', 'Package_TO_SOT_SMD:SOT-23', {'1': 'Q1_G', '2': '+12V', '3': 'VIN_F'}, 'C15127',
      'Reverse-polarity protection'),
    P('D2', 'Device:D_Zener', 'BZT52C10', 'Diode_SMD:D_SOD-123', {'1': '+12V', '2': 'Q1_G'}, desc='Vgs clamp'),
    R('R1', '10k', 'Q1_G', 'GND', 'C25804'),
    P('D3', 'Device:D_Schottky', 'SS34', 'Diode_SMD:D_SMA', {'1': '+12V', '2': 'VBUS'}, 'C8678', 'USB power OR'),
    P('C1', 'Device:C_Polarized', '100u 35V', 'Capacitor_SMD:CP_Elec_8x10.5', {'1': '+12V', '2': 'GND'}),
    C('C2', '10u 25V', '+12V', 'GND', 'C15850', FP['C0805']),
    C('C3', '10u 25V', '+12V', 'GND', 'C15850', FP['C0805']),
    P('U1', 'Regulator_Switching:AP63203WU', 'AP63203WU', 'Package_TO_SOT_SMD:TSOT-23-6',
      {'1': '+3V3', '2': '+12V', '3': '+12V', '4': 'GND', '5': 'SW', '6': 'BST'}, 'C780769'),
    C('C4', '100n', 'BST', 'SW', 'C14663'),
    P('L1', 'Device:L', '4.7u 3A', 'Inductor_SMD:L_Bourns_SRN6045TA', {'1': 'SW', '2': '+3V3'}),
    C('C5', '22u', '+3V3', 'GND', 'C45783', FP['C0805']),
    C('C6', '22u', '+3V3', 'GND', 'C45783', FP['C0805']),
    P('F2', 'Device:Polyfuse', '0.5A', 'Fuse:Fuse_1206_3216Metric', {'1': '+12V', '2': 'RG_PWR'}, desc='RG-15 supply'),
]))

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

# ── ESP32-S3 ──────────────────────────────────────────────────────────────────
esp = {'1': 'GND', '40': 'GND', '41': 'GND', '2': '+3V3', '3': 'EN',
       '27': 'BOOT', '13': 'USB_DN', '14': 'USB_DP',
       '12': 'SDA', '17': 'SCL',
       '11': 'GPS_RX', '10': 'GPS_TX',
       '9': 'RG_RX', '8': 'RG_TX',
       '5': 'WIND_SPD', '4': 'WIND_DIR',
       '24': 'LED',
       '6': 'AUX1', '7': 'AUX2', '18': 'AUX3', '19': 'AUX4',
       '36': 'U0RXD', '37': 'U0TXD'}
for n in range(1, 42):
    esp.setdefault(str(n), None)
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
    P('D4', 'Device:LED', 'STATUS', 'LED_SMD:LED_0603_1608Metric', {'1': 'GND', '2': 'LED_A'}, 'C72043'),
    P('TP1', 'Connector:TestPoint', 'U0RXD', 'TestPoint:TestPoint_Pad_D1.5mm', {'1': 'U0RXD'}),
    P('TP2', 'Connector:TestPoint', 'U0TXD', 'TestPoint:TestPoint_Pad_D1.5mm', {'1': 'U0TXD'}),
    P('TP3', 'Connector:TestPoint', 'GND', 'TestPoint:TestPoint_Pad_D1.5mm', {'1': 'GND'}),
    P('TP4', 'Connector:TestPoint', '3V3', 'TestPoint:TestPoint_Pad_D1.5mm', {'1': '+3V3'}),
]))

# ── I2C sensor ports ──────────────────────────────────────────────────────────
XH4 = 'Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical'
i2c = [P(f'J{n}', 'Connector_Generic:Conn_01x04', name, XH4, {'1': 'GND', '2': '+3V3', '3': 'SDA', '4': 'SCL'}, 'C144395',
         'JST-XH: 1 GND, 2 3V3, 3 SDA, 4 SCL')
       for n, name in ((3, 'I2C TSL2591'), (4, 'I2C MLX90614'), (5, 'I2C BME280'), (6, 'I2C SPARE'))]
blocks.append(('I2C sensor ports (identical pinout)', i2c + [
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
      {'1': 'GND', '2': 'RG_PWR', '3': 'RG_TXO', '4': 'RG_RXI'}, desc='Pluggable 3.5 mm: 1 GND, 2 V+ (12 V), 3 RG TX, 4 RG RX'),
    R('R11', '100', 'RG_TXO', 'RG_RX', 'C22775'),
    R('R12', '100', 'RG_TX', 'RG_RXI', 'C22775'),
    P('U5', 'Power_Protection:USBLC6-2SC6', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6',
      {'1': 'RG_TXO', '6': 'RG_TXO', '3': 'RG_RXI', '4': 'RG_RXI', '2': 'GND', '5': '+3V3'}, 'C7519', 'RG-15 ESD'),
]))

# ── Wind ──────────────────────────────────────────────────────────────────────
blocks.append(('Wind: anemometer + vane', [
    P('J9', 'Connector_Generic:Conn_01x05', 'WIND', 'Connector_Phoenix_MC:PhoenixContact_MC_1,5_5-G-3.5_1x05_P3.50mm_Horizontal',
      {'1': 'WSPD_EXT', '2': 'GND', '3': 'WDIR_EXT', '4': 'GND', '5': '+3V3'},
      desc='Pluggable 3.5 mm: 1 SPD, 2 GND, 3 DIR, 4 GND, 5 3V3 (pot vane excitation)'),
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
    P('J10', 'Connector_Generic:Conn_01x06', 'AUX', 'Connector_JST:JST_XH_B6B-XH-A_1x06_P2.50mm_Vertical',
      {'1': 'GND', '2': '+3V3', '3': 'AUX1', '4': 'AUX2', '5': 'AUX3', '6': 'AUX4'},
      desc='JST-XH: 1 GND, 2 3V3, 3 IO6, 4 IO7, 5 IO10, 6 IO11'),
] + [P(f'H{n}', 'Mechanical:MountingHole', 'M3', 'MountingHole:MountingHole_3.2mm_M3', {}) for n in range(1, 5)]))

FLAGS = ['GND', '+12V', '+3V3', 'VBUS']
