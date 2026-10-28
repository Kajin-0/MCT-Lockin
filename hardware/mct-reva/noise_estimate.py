"""First-order nominal white-noise estimate at 1 kHz, NOT an experimental result.
Case assumes ADC SNR 111 dBFS full scale 5Vpp DIFFERENTIAL, 20 kHz ENBW;
noise coefficients from TI typical values. Excludes flicker / G-R, bias and interference.
"""
from math import sqrt, log10, pi
k=1.380649e-23
Troom=300.0
vfs_rms=5/(2*sqrt(2)) # 5 Vpp differential
adc_dens=vfs_rms/10**(111/20)/sqrt(20_000)
for temp in [77,200]:
 for rdet in [10,50,200]:
  g=51
  rprot=22
  rfb=1000
  rg=20
  bdrv_noise=sqrt(2*(sqrt(4*k*Troom*10_000))**2 + (2*1.1e-9)**2 +(1.7e-12*10_000)**2)
  contributions={
    'detector_Johnson':sqrt(4*k*temp*rdet),
    'input_series_R22':sqrt(4*k*Troom*rprot),
    'amplifier_vn_1kHz':1.1e-9,
    'amplifier_in_Rdet':1.7e-12*rdet,
    'gain_resistor':sqrt(4*k*Troom*rg),
    'feedback_Rf_referred':sqrt(4*k*Troom*rfb)/g,
    'ADC_driver_referred':bdrv_noise/g,
    'ADC_referred':adc_dens/g
  }
  n=sqrt(sum(v*v for v in contributions.values()))
  print(f'{temp=}K {rdet=} ohm, 1kHz electronic+Johnson nominal {n*1e9:.3f} nV/sqrt(Hz); excluding detector noise: {sqrt(sum(v*v for q,v in contributions.items() if q!="detector_Johnson"))*1e9:.3f}')
print('WARNING: the real biased-detector noise and bias-source noise may greatly exceed this estimate.')
