"""Add power net classes to the KiCad project file."""
import json, sys, copy
f = sys.argv[1]
d = json.load(open(f))
ns = d['net_settings']
base = next(c for c in ns['classes'] if c['name'] == 'Default')
def cls(name, width, clearance, via=0.8, drill=0.4):
    c = copy.deepcopy(base); c.update(name=name, track_width=width, clearance=clearance, via_diameter=via, via_drill=drill, priority=0)
    return c
ns['classes'] = [base, cls('Power', 0.6, 0.2), cls('Supply3V3', 0.4, 0.2, 0.6, 0.3), cls('USB', 0.2, 0.15, 0.6, 0.3), cls('USBPower', 0.35, 0.15, 0.6, 0.3)]
ns['netclass_patterns'] = [{'netclass': 'Power', 'pattern': p} for p in ('+12V', '/VIN_RAW', '/VIN_F', '/RG_PWR', '/SW', '+5V', '/DK_5V')] + \
    [{'netclass': 'Supply3V3', 'pattern': p} for p in ('+3V3', 'GND')] + \
    [{'netclass': 'USB', 'pattern': p} for p in ('/USB_DP', '/USB_DN')] + [{'netclass': 'USBPower', 'pattern': 'VBUS'}]
# KiCad's TrueType stroke check flags every size of the variable Inter font; stroke widths were measured
# on the plotted gerbers instead (see genpcb.py, FONT).
d['board']['design_settings'].setdefault('rule_severities', {})['text_thickness'] = 'ignore'
json.dump(d, open(f, 'w'), indent=2)
print('classes:', [c['name'] for c in ns['classes']])
