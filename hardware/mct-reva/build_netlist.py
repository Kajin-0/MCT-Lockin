"""Generate auditable MCT-LIA Mini Rev A capture-stage pin-to-net and KiCad netlist draft.
No external dependencies. This file does not claim to have passed KiCad ERC.
"""
from collections import defaultdict
from pathlib import Path
import csv, json, re, datetime
root=Path(__file__).resolve().parent
C={}
def add(ref,value,footprint,pins,note='',state='prototype'):
    assert ref not in C
    assert len(pins)==len(set(pins))
    C[ref]=dict(value=value, footprint=footprint, pins={str(a):b for a,b in pins.items()}, note=note, state=state)
R='Resistor_SMD:R_0805_2012Metric';Rsmall='Resistor_SMD:R_0603_1608Metric';Csmall='Capacitor_SMD:C_0603_1608Metric';C0805='Capacitor_SMD:C_0805_2012Metric'
# External Kelvin detector and off-board safely limited bias supply
add('J1','MCT_KELVIN_4WAY','Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical',{'1':'BIAS_FORCE_P','2':'AGND','3':'DET_SENSE_P','4':'DET_SENSE_N'},'Physical connector / footprint unselected; external Kelvin wiring joins force and sense at detector', 'boundary')
add('J2','EXTERNAL_CURRENT_LIMITED_BIAS','Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',{'1':'BIAS_FORCE_P','2':'AGND'},'External 0..3V supply MUST have independent <=50mA limit; no protection on board', 'boundary')
add('R1','22R',Rsmall,{'1':'DET_SENSE_P','2':'INPUT_PROTECTED'},'Source series protection; contributes ~0.60 nV/sqrt(Hz) at 300K')
add('R2','0R',Rsmall,{'1':'DET_SENSE_N','2':'AGND'},'Sense return star / Kelvin link, layout critical')
add('C1','4.7uF_10V_X7R',C0805,{'1':'INPUT_PROTECTED','2':'AMP_AC_IN'},'Effective DC-bias-adjusted capacitance must be checked; X7R MLCC nonlinear with bias')
add('R3','47k',Rsmall,{'1':'AMP_AC_IN','2':'AGND'},'DC bias return. With 4.7uF nominal, high pass ~0.72 Hz. High input resistance vs 200R source, but bipolar opamp DC input bias can saturate on high gain; verify at worst case')
# low noise dual opamp, SOIC-8 TI verified pin map
add('U1','OPA1612AID','Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',{1:'AMP_OUT',2:'AFE_FB',3:'AMP_AC_IN',4:'AVEE_N5',5:'ADC_VCOML',6:'ADC_B_SUM',7:'ADC_B_OUT',8:'AVDD_P5'},'SOIC-8 physical pinout verified against TI datasheet (OPA1612 not OPA1611)')
add('R4','1k',Rsmall,{'1':'AMP_OUT','2':'AFE_FB'},'Non-inverting first stage feedback')
add('R5','20R',Rsmall,{'1':'AFE_FB','2':'AGND'},'Fixed gain G=51')
add('R6','6.65R',Rsmall,{'1':'AFE_FB','2':'GAIN201_SWITCH'},'When switch closed R5||R6=>G~201.4')
add('SW1','GAIN_SELECT_NO','Jumper:SolderJumper-2_P1.3mm_Open',{'1':'GAIN201_SWITCH','2':'AGND'},'Solder jumper closed selects G~201; open selects G51; physical design review required','prototype')
# first analog pole before gain-1 ADC level shifting stage, AC coupling eliminates DC amp error
add('R7','330R',Rsmall,{'1':'AMP_OUT','2':'FILTER_STAGE1'},'Anti-alias stage 1')
add('C2','15nF',Csmall,{'1':'FILTER_STAGE1','2':'AGND'},'Pole ~32.2 kHz')
add('C3','10uF_10V_X7R',C0805,{'1':'FILTER_STAGE1','2':'ADC_AC_COUPLED'},'AC-couple to inverting ADC level shifter, at 2.5V common mode')
add('R8','10k',Rsmall,{'1':'ADC_AC_COUPLED','2':'ADC_B_SUM'},'Inverting driver Rin')
add('R9','10k',Rsmall,{'1':'ADC_B_SUM','2':'ADC_B_OUT'},'Inverting driver gain ~-1')
add('C4','470pF_C0G',Csmall,{'1':'ADC_B_SUM','2':'ADC_B_OUT'},'Second analog low pass pole ~33.9 kHz')
add('R10','47R',Rsmall,{'1':'ADC_B_OUT','2':'ADC_LMINUS'},'PCM1804 input drive resistor')
add('R11','47R',Rsmall,{'1':'ADC_VCOML','2':'ADC_LPLUS'},'PCM1804 L+ input held to VCOML (single-sided differential ADC drive)')
add('C5','10nF_C0G',Csmall,{'1':'ADC_LPLUS','2':'ADC_LMINUS'},'ADC differential charge kickback filter; verify against TI input drive model')
# Right channel quiet diagnostic
add('R12','47R',Rsmall,{'1':'ADC_VCOMR','2':'ADC_RPLUS'},'Quiet channel +, noise monitor')
add('R13','47R',Rsmall,{'1':'ADC_VCOMR','2':'ADC_RMINUS'},'Quiet channel -, noise monitor')
add('C6','10nF_C0G',Csmall,{'1':'ADC_RPLUS','2':'ADC_RMINUS'})
# ADC PCM1804 28 SSOP verified pin numbers and I2S master options
adc={1:'ADC_VREFL',2:'AGND',3:'ADC_VCOML',4:'ADC_LPLUS',5:'ADC_LMINUS',6:'D3V3',7:'DGND',8:'DGND',9:'D3V3',10:'D3V3',11:'DGND',12:'DGND',13:'DGND',14:'D3V3',15:'MCU_I2S_DATA',16:'MCU_I2S_BCK',17:'MCU_I2S_LRCK',18:'ADC_MCLK',19:'MCU_ADC_RESET',20:'ADC_OVFR',21:'ADC_OVFL',22:'AVDD_ADC5',23:'AGND',24:'ADC_RMINUS',25:'ADC_RPLUS',26:'ADC_VCOMR',27:'AGND',28:'ADC_VREFR'}
add('U2','PCM1804DB','Package_SO:SSOP-28_5.3x10.2mm_P0.65mm',adc,'48kHz fs master I2S: 12.288MHz MCLK, OSR2,1,0=0,1,1; FMT1,FMT0=0,1; BYPAS=0')
# datasheet recommended reference decoupling
for ref,net,value,fp in [('C7','ADC_VREFL','10uF_10V',C0805),('C8','ADC_VREFL','100nF',Csmall),('C9','ADC_VREFR','10uF_10V',C0805),('C10','ADC_VREFR','100nF',Csmall),('C11','ADC_VCOML','100nF',Csmall),('C12','ADC_VCOMR','100nF',Csmall),('C13','AVDD_P5','100nF',Csmall),('C14','AVDD_P5','10uF',C0805),('C15','AVEE_N5','100nF',Csmall),('C16','AVEE_N5','10uF',C0805),('C17','AVDD_ADC5','100nF',Csmall),('C18','AVDD_ADC5','10uF',C0805),('C19','D3V3','100nF',Csmall),('C20','D3V3','10uF',C0805)]:
 add(ref,value,fp,{'1':net,'2':'AGND' if net not in ['D3V3'] else 'DGND'},'Place next to IC; PCM1804 analog and digital grounds must have controlled connection')
# local AGND/DGND single point; confirm plane and return current physical approach
add('R14','0R',Rsmall,{'1':'AGND','2':'DGND'},'Single star point provisional; footprint placement controls actual return loop')
# oscillator master 12.288MHz; master clock bit clock frame clock out of PCM
add('U3','ASEM1-12.288MHZ-L','Oscillator:Oscillator_SMD_Abracon_ASEM1-4Pin_3.2x2.5mm',{1:'D3V3',2:'DGND',3:'CLK_SOURCE',4:'D3V3'},'Pin map 1=OE 2=GND 3=OUT 4=VDD; exact library footprint to be verified','footprint-review')
add('R15','33R',Rsmall,{'1':'CLK_SOURCE','2':'ADC_MCLK'},'MCLK series damping, PCB layout required')
add('C21','100nF',Csmall,{'1':'D3V3','2':'DGND'},'Dedicated near oscillator')
add('R16','100k',Rsmall,{'1':'MCU_ADC_RESET','2':'DGND'},'PCM1804 /RST held low during startup until firmware releases it')
# reference I/O
add('J3','EXT_REF_TTL_3V3','Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',{'1':'EXT_REF_CON','2':'AGND'},'BNC connector footprint placeholder, TTL 0..3.3V, no analog sine', 'placeholder')
add('R17','1k',Rsmall,{'1':'EXT_REF_CON','2':'MCU_EXT_REF'},'MCU digital capture input, pending clamp/ESD specification')
add('R18','100k',Rsmall,{'1':'MCU_EXT_REF','2':'DGND'},'logic pull-down')
add('J4','INT_REF_TTL_3V3','Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',{'1':'INT_REF_CON','2':'AGND'},'BNC connector footprint placeholder, >=10k load only','placeholder')
add('R19','100R',Rsmall,{'1':'MCU_INT_REF','2':'INT_REF_CON'},'3.3V MCU output series resistor; do not drive 50-ohm loads')
# MCU / supply board abstraction. Nucleo mating pin mapping NOT established.
board={1:'AVDD_P5',2:'AVEE_N5',3:'AVDD_ADC5',4:'D3V3',5:'AGND',6:'DGND',7:'MCU_I2S_BCK',8:'MCU_I2S_LRCK',9:'MCU_I2S_DATA',10:'MCU_ADC_RESET',11:'MCU_EXT_REF',12:'MCU_INT_REF',13:'ADC_OVFL',14:'ADC_OVFR'}
add('J5','MCU_AND_POWER_INTERFACE','Connector_PinHeader_2.54mm:PinHeader_2x07_P2.54mm_Vertical',board,'Interface pin numbering is electrical-only; connector orientation and actual STM32 pin mapping are NOT verified','boundary')
# write pin connections and nets
nets=defaultdict(list)
for ref,item in C.items():
 for pin,net in item['pins'].items():
  assert re.match(r'^[A-Za-z0-9_]+$',net)
  nets[net].append((ref,pin))
with (root/'PIN_NET_CONNECTIONS.csv').open('w',newline='') as f:
 w=csv.writer(f,lineterminator='\n'); w.writerow(['ref','part','physical_pin','net','value','footprint','status','notes'])
 for ref,i in C.items():
  for p,n in sorted(i['pins'].items(),key=lambda a:int(a[0])):
   w.writerow([ref,ref,int(p),n,i['value'],i['footprint'],i['state'],i['note']])
with (root/'NET_SUMMARY.csv').open('w',newline='') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['net','connections','node_count'])
 for net,pins in sorted(nets.items()):w.writerow([net,'; '.join(ref+':'+pin for ref,pin in pins),len(pins)])
with (root/'COMPONENTS.csv').open('w',newline='') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['reference','value','footprint_candidate','status','engineering_note'])
 for ref,i in C.items():w.writerow([ref,i['value'],i['footprint'],i['state'],i['note']])
# Kicad-style s-expression netlist (draft; KiCad not installed here)
def esc(s):return '"'+str(s).replace('\\','\\\\').replace('"','\\"')+'"'
def s_atom(s):return str(s)
lines=['(export (version "E")','  (design (source "mct_lia_mini_reva_capture") (date "2026-10-27") (tool "MCT-LIA pin-map generator"))','  (components']
for ref,i in C.items():
 lines += [f'    (comp (ref {esc(ref)}) (value {esc(i["value"])}) (footprint {esc(i["footprint"])}) (tstamp {esc("MCTLIA_REVA_"+ref)}))']
lines+=['  )','  (nets']
for k,(name,pins) in enumerate(sorted(nets.items()),1):
 lines.append(f'    (net (code {esc(k)}) (name {esc(name)})')
 for ref,p in sorted(pins,key=lambda a:(a[0],int(a[1]))):lines.append(f'      (node (ref {esc(ref)}) (pin {esc(p)}))')
 lines.append('    )')
lines+=['  )',')']
(root/'MCT_LIA_Mini_RevA.net').write_text('\n'.join(lines)+'\n')
(root/'MCT_LIA_Mini_RevA.json').write_text(json.dumps({'revision':'Rev A capture draft','components':C,'nets':{k:v for k,v in nets.items()}},indent=2)+'\n')
# check pins verified for U1 & U2, net connectivity, component relationships
assert len(C['U1']['pins'])==8 and len(C['U2']['pins'])==28
assert C['U1']['pins']['8']=='AVDD_P5' and C['U1']['pins']['4']=='AVEE_N5'
assert C['U2']['pins']['18']=='ADC_MCLK' and C['U2']['pins']['15']=='MCU_I2S_DATA'
assert C['U2']['pins']['8']=='DGND' and C['U2']['pins']['6']=='D3V3'
assert any(r=='U1' and p=='2' for r,p in nets['AFE_FB'])
assert len(nets['BIAS_FORCE_P'])==2
assert len(nets['AGND'])>10
assert all(len(pins)>=2 for name,pins in nets.items()),[name for name,pins in nets.items() if len(pins)<2]
print(f'{len(C)} components; {len(nets)} nets; {sum(len(v) for v in nets.values())} pins; {len(lines)} netlist lines')
