import uuid,math,csv,json,pathlib,html
p=pathlib.Path('/mnt/data/lockin_reva')
uid=lambda: str(uuid.uuid4())
rootid=uid()
fmt=lambda v: f'{v:.3f}'.rstrip('0').rstrip('.') if isinstance(v,float) else str(v)
def esc(s):return str(s).replace('\\','\\\\').replace('"','\\"').replace('\n',' ')
def q(s):return '"'+esc(s)+'"'
font='(effects (font (size 1.0 1.0)))'
def defn(name, pins, graphics='',width=10,height=5):
    r='\n    (symbol '+q('Lockin:'+name)+' (pin_numbers (hide yes)) (pin_names (offset 0.3)) (in_bom yes) (on_board yes)\n'
    r+=f'      (property "Reference" "U" (at 0 {height+3} 0) {font})\n'
    r+=f'      (property "Value" {q(name)} (at 0 {-height-3} 0) {font})\n'
    r+=f'      (symbol {q(name+"_0_1")} {graphics if graphics else f"(rectangle (start {-width} {-height}) (end {width} {height}) (stroke (width 0.254) (type default)) (fill (type background)))"})\n'
    r+=f'      (symbol {q(name+"_1_1")}\n'
    for no,lab,px,py,angle,typ in pins:
        r+=f'       (pin {typ} line (at {fmt(px)} {fmt(py)} {angle}) (length 2.54) (name {q(lab)} {font}) (number {q(no)} {font}))\n'
    r+='      )\n    )'
    return r
parts={}
# component geometry pin endpoints in lib coords
LR=[('1','1',-7.54,0,0,'passive'),('2','2',7.54,0,180,'passive')]
parts['R']=defn('R',LR,'(rectangle (start -5 -1.8) (end 5 1.8) (stroke (width 0.254) (type default)) (fill (type background)))',5,1.8)
parts['C']=defn('C',LR,'(polyline (pts (xy -0.75 -3) (xy -0.75 3)) (stroke (width 0.35) (type default)) (fill (type none))) (polyline (pts (xy 0.75 -3) (xy 0.75 3)) (stroke (width 0.35) (type default)) (fill (type none)))',5,3)
parts['FB']=defn('FB',LR,'(rectangle (start -5 -2.2) (end 5 2.2) (stroke (width 0.254) (type default)) (fill (type background)))',5,2.2)
parts['JP']=defn('JP',LR,'(rectangle (start -5 -2) (end 5 2) (stroke (width 0.254) (type default)) (fill (type background)))',5,2)
parts['D']=defn('D',LR,'(polyline (pts (xy -3 -3) (xy -3 3)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy -2.8 -3) (xy 3 0) (xy -2.8 3) (xy -2.8 -3)) (stroke (width 0.254) (type default)) (fill (type none)))',5,3)
# OPA1656 pin map, axes local +y upward
pinsU=[('3','INA+',-17.54,9,0,'input'),('2','INA-',-17.54,3,0,'input'),('1','OUTA',17.54,6,180,'output'),('5','INB+',-17.54,-5,0,'input'),('6','INB-',-17.54,-11,0,'input'),('7','OUTB',17.54,-8,180,'output'),('8','V+',0,21.54,270,'power_in'),('4','V-',0,-21.54,90,'power_in')]
parts['OPA1656']=defn('OPA1656',pinsU,'(rectangle (start -15 -19) (end 15 19) (stroke (width 0.254) (type default)) (fill (type background)))',15,19)
parts['BNC']=defn('BNC',[('1','SIG',-9.54,3,0,'passive'),('2','SHIELD',-9.54,-3,0,'passive')],width=7,height=7)
headerpins=[(str(i+1),nm,-13.54,13-i*5.5,0,'passive') for i,nm in enumerate(['USB_5V','3V3','GND','ADC','EXT_REF','INT_REF'])]
parts['HDR6']=defn('HDR6',headerpins,width=11,height=18)
# active circuit components
components=[]
def comp(ref,lib,value,x,y,nets,footprint='',datasheet='',mpn='',note=''):
    assert len(nets)==len([x for x in {'OPA1656':pinsU,'BNC':[1,2],'HDR6':headerpins}.get(lib,LR)])
    components.append(dict(ref=ref,lib=lib,value=value,x=x,y=y,nets=nets,footprint=footprint,datasheet=datasheet,mpn=mpn,note=note))
resfoot='Resistor_SMD:R_0805_2012Metric';capfoot='Capacitor_SMD:C_0805_2012Metric'
bigcap='Capacitor_SMD:C_1210_3225Metric'
bncfoot='Connector_Coaxial:Amphenol_112404_Horizontal'
comp('J1','BNC','SIGNAL_IN_BNC',34,42,['VIN','AGND'],bncfoot,note='BNC footprint is illustrative; verify actual connector mating and pad numbers')
comp('R1','R','1k',74,42,['VIN','PROT_IN'],resfoot,note='Input current limiting; noise contributor')
comp('C1','C','10uF X7R 25V',106,42,['PROT_IN','AC_IN'],bigcap,note='Check effective capacitance under 1.65 V bias')
comp('R2','R','49.9R',74,70,['TERM_TAP','AGND'],resfoot)
comp('JP1','JP','OPTIONAL_50R_TERM',34,70,['VIN','TERM_TAP'], 'Jumper:SolderJumper-2_P1.3mm_Open',note='OPEN default; closed -> 49.9ohm BNC termination')
comp('R3','R','1M',134,71,['VBIAS','AC_IN'],resfoot)
comp('U1','OPA1656','OPA1656IDR',180,126,['AC_IN','FB_A','AMP_OUT','VDIV','VBIAS','VBIAS','AVDD5','AGND'],'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm','https://www.ti.com/product/OPA1656','OPA1656IDR',note='A: gain 1/11/101. B: 1.65V midpoint buffer')
comp('R4','R','10k 0.1%',230,83,['AMP_OUT','FB_A'],resfoot)
comp('R5','R','100R 0.1%',230,102,['FB_A','G101_TAP'],resfoot)
comp('JP2','JP','GAIN_101',265,102,['G101_TAP','VBIAS'],'Jumper:SolderJumper-2_P1.3mm_Open')
comp('R6','R','1k 0.1%',230,119,['FB_A','G11_TAP'],resfoot)
comp('JP3','JP','GAIN_11',265,119,['G11_TAP','VBIAS'],'Jumper:SolderJumper-2_P1.3mm_Open')
comp('R7','R','47R',231,157,['AMP_OUT','AA1'],resfoot)
comp('C2','C','10nF C0G',265,175,['AA1','AGND'],capfoot)
comp('R8','R','47R',298,157,['AA1','AA2'],resfoot)
comp('C3','C','10nF C0G',332,175,['AA2','AGND'],capfoot)
comp('R9','R','330R',362,157,['AA2','ADC_IN'],resfoot)
comp('D1','D','BAT54WS_A',369,184,['3V3','ADC_IN'],'Diode_SMD:D_SOD-323',note='D1 cathode=3V3 (pin1), anode=ADC_IN(pin2); verify clamp injection current and pad polarity')
comp('D2','D','BAT54WS_B',398,184,['ADC_IN','AGND'],'Diode_SMD:D_SOD-323',note='D2 cathode=ADC_IN(pin1), anode=AGND(pin2)')
comp('J2','HDR6','NUCLEO_G474RE_IO',376,48,['USB5V','3V3','AGND','ADC_IN','REF_CAPTURE','REF_DRIVE'],'Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical',note='Header-to-Nucleo mapping must be finalized in CubeMX/NUCLEO schematics')
comp('J3','BNC','EXT_REF_TTL_BNC',34,208,['EXT_REF_BNC','AGND'],bncfoot,note='0-3.3 V CMOS/TTL square wave only')
comp('R10','R','1k',80,205,['EXT_REF_BNC','REF_CAPTURE'],resfoot)
comp('R11','R','100k',114,227,['REF_CAPTURE','AGND'],resfoot)
comp('D3','D','BAT54WS_C',148,227,['3V3','REF_CAPTURE'],'Diode_SMD:D_SOD-323')
comp('D4','D','BAT54WS_D',180,227,['REF_CAPTURE','AGND'],'Diode_SMD:D_SOD-323')
comp('J4','BNC','INT_REF_TTL_BNC',290,208,['INT_REF_TTL','AGND'],bncfoot,note='3.3V logic output for high-impedance loads; NOT 50-ohm loaded 3.3 V source')
comp('R12','R','100R',251,205,['REF_DRIVE','INT_REF_TTL'],resfoot)
comp('FB1','FB','600R@100MHz',34,267,['USB5V','AVDD5'],'Inductor_SMD:L_0805_2012Metric')
comp('C4','C','10uF 10V',72,266,['AVDD5','AGND'],bigcap)
comp('C5','C','100nF 25V',107,266,['AVDD5','AGND'],capfoot)
comp('R13','R','10k',165,263,['3V3','VDIV'],resfoot)
comp('R14','R','10k',203,263,['VDIV','AGND'],resfoot)
comp('C6','C','47uF 6.3V',238,263,['VDIV','AGND'],bigcap)
comp('C7','C','100nF 25V',283,263,['3V3','AGND'],capfoot)
# labels for pin direct. Kicad width in A2 594; x <420
libs='\n'.join(parts.values())
sc=[]
net_pin_counts={}
for c in components:
    x,y=c['x'],c['y'];lib=c['lib'];ref=c['ref']
    pins={'OPA1656':pinsU,'BNC':[('1','',-9.54,3,0,'passive'),('2','',-9.54,-3,0,'passive')],'HDR6':headerpins}.get(lib,LR)
    inst=f'(symbol (lib_id {q("Lockin:"+lib)}) (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {q(uid())})\n'
    refx=x;refy=y+(4 if lib not in ('OPA1656','BNC','HDR6') else -23)
    inst+=f'  (property "Reference" {q(ref)} (at {fmt(refx)} {fmt(refy-3)} 0) {font})\n'
    inst+=f'  (property "Value" {q(c["value"])} (at {fmt(refx)} {fmt(refy)} 0) {font})\n'
    if c['footprint']: inst+=f'  (property "Footprint" {q(c["footprint"])} (at {x} {y} 0) {font} (hide yes))\n'
    if c['datasheet']: inst+=f'  (property "Datasheet" {q(c["datasheet"])} (at {x} {y} 0) {font} (hide yes))\n'
    for index,pn in enumerate(pins):
        no,lab,px,py,ang,typ=pn
        net=c['nets'][index];net_pin_counts.setdefault(net,[]).append(ref+':'+no)
        inst+=f'  (pin {q(no)} (uuid {q(uid())}))\n'
        lx=x+px;ly=y-py
        # labels located exactly at the electrical pin endpoint. KiCad nets are defined via attached labels.
        sc.append(f'(label {q(net)} (at {fmt(lx)} {fmt(ly)} 0) {font} (uuid {q(uid())}))')
    inst+=f'  (instances (project "lockin_reva_afe" (path "/{rootid}" (reference {q(ref)}) (unit 1))))\n)'
    sc.append(inst)
header=f'(kicad_sch (version 20231120) (generator "eeschema")\n (uuid {q(rootid)}) (paper "A2")\n (title_block (title "USB Lock-in Amplifier - Rev A Analog Front-End") (date "2026-10-27") (rev "0.1 DRAFT") (company "Engineering prototype - NOT production approved") (comment 1 "STM32G474 Nucleo interface: pin mapping provisional") (comment 2 "Input 50 ohm source; JP1 optional termination; gain jumpers mutually exclusive"))\n (lib_symbols\n'+libs+'\n )\n'
schematic=header+'\n'.join(sc)+'\n (embedded_fonts no)\n)\n'
(p/'lockin_reva_afe.kicad_sch').write_text(schematic)
# Generate BOM with traceability to schematic
with (p/'BOM_draft.csv').open('w',newline='') as f:
    writer=csv.writer(f);writer.writerow(['Designator','Value','Proposed MPN','Footprint (provisional)','Source notes / restrictions'])
    for c in components: writer.writerow([c['ref'],c['value'],c['mpn'],c['footprint'],c['note']])
with (p/'NET_CONNECTIONS.csv').open('w',newline='') as f:
    writer=csv.writer(f);writer.writerow(['Net','Connected pins','Count'])
    for net,loc in sorted(net_pin_counts.items()):writer.writerow([net,', '.join(loc),len(loc)])
# verify static design, for obvious short/disconnected net mistakes
assert all(len(l)>1 for k,l in net_pin_counts.items()),[k for k,l in net_pin_counts.items() if len(l)==1]
assert {c['ref'] for c in components}==set(c['ref'] for c in components)
# balanced parens outside quoted strings
inside=False;escape=False;depth=0
for c in schematic:
    if inside:
        if escape:escape=False
        elif c=='\\':escape=True
        elif c=='"':inside=False
    else:
        if c=='"':inside=True
        elif c=='(':depth+=1
        elif c==')':depth-=1;assert depth>=0
assert depth==0 and not inside
print('Wrote schematic with',len(components),'components,',len(net_pin_counts),'nets;',len(schematic),'bytes; syntactic balance OK')
print('NETS',net_pin_counts)
