"""Reproducible first-order estimate; engineering model, not empirical validation."""
import math
K = 1.380649e-23
T = 300.0
Rsource, Rseries, Rg, Rbias = 50.0, 1000.0, 100.0, 1e6
Cac = 10e-6
fs=1e6
G=101.0
Vfs=3.3
SINAD=65.6
Tmeas=10.0

def thermal(R): return (4*K*T*R)**0.5

def bias_thermal_to_input(f):
    Zc = complex(0, -1/(2*math.pi*f*Cac))
    Zs=Rsource+Rseries+Zc
    return thermal(Rbias)*abs(Zs/(Rbias+Zs))

adc_err=(Vfs/(2*math.sqrt(2)))/(10**(SINAD/20))
adc_asd=adc_err / math.sqrt(fs/2)/G
print('First-order estimates (not guaranteed physical performance):')
for f in (1,10,1000,100000):
    ea=4.3e-9 if f>=1000 else 8e-9 # 8nV example low-f assumption, NOT datasheet-backed
    evbias=5e-9 # illustrative, MUST measure
    ei=math.sqrt(sum(v*v for v in (thermal(Rsource),thermal(Rseries),thermal(Rg),bias_thermal_to_input(f),ea,evbias,adc_asd)))
    estimated=ei*math.sqrt(1/(2*Tmeas))
    print(f'{f:>7} Hz : input ASD ~{ei*1e9:.1f} nV/sqrtHz, 10s quadrature sigma ~{estimated*1e9:.2f} nVrms, idealized SNR(1uV)={1e-6/estimated:.0f}')
    if f == 100000: pass
print('ADC input referred noise density from typical SINAD, white approximation:',adc_asd*1e9,'nV/sqrtHz')
print('HP cutoff, nominal:',1/(2*math.pi*Rbias*Cac),'Hz')
for f in (1,10000,100000,500000):
    x=2*math.pi*f*47*10e-9
    H=1/complex(1-x*x,3*x)
    print('LPF at',f,'Hz: ',20*math.log10(abs(H)),'dB,',math.degrees(math.atan2(H.imag,H.real)),'degrees')
