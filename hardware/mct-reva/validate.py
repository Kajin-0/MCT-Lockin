"""Lightweight structural checks; NOT electrical-rule checking."""
import csv, json, pathlib
root=pathlib.Path(__file__).resolve().parent
j=json.loads((root/'MCT_LIA_Mini_RevA.json').read_text())
parts=j['components']; nets=j['nets']; pins=sum(len(v['pins']) for v in parts.values())
assert len(parts)==len(set(parts))
assert pins==sum(len(v) for v in nets.values())
assert all(len(nodes)>=2 for nodes in nets.values())
assert all(parts[ref]['pins'][p]==n for n,nodes in nets.items() for ref,p in nodes)
assert parts['U1']['pins']=={'1':'AMP_OUT','2':'AFE_FB','3':'AMP_AC_IN','4':'AVEE_N5','5':'ADC_VCOML','6':'ADC_B_SUM','7':'ADC_B_OUT','8':'AVDD_P5'}
assert parts['U2']['pins']['22']=='AVDD_ADC5'
assert parts['U2']['pins']['18']=='ADC_MCLK'
net=(root/'MCT_LIA_Mini_RevA.net').read_text(); level=0; quoted=False; escaped=False
for ch in net:
 if ch=='\\' and quoted and not escaped:escaped=True;continue
 if ch=='"' and not escaped:quoted=not quoted
 if not quoted and ch=='(':level+=1
 if not quoted and ch==')':level-=1
 assert level>=0
 escaped=False
assert level==0 and not quoted
print('PASS: unique ref/pin, every net >=2 nodes, verified U1/U2 pin maps, balanced KiCad-style netlist')
print(f'COMPONENTS {len(parts)} NETS {len(nets)} PINS {pins}')
