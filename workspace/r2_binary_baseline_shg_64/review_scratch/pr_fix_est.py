import sys,math,json
sys.path.insert(0,'.')
import numpy as np
from src.reconciliation.real_polar_sc_rescue import polar_encode_non_systematic as enc, polar_sc_decode_with_frozen as scd, _polar_weight_order
from src.reconciliation.cpp_scl_wrapper import PolarSCLDecoder
N=4096;nl=12;rng=np.random.default_rng(7);dec=PolarSCLDecoder();order=_polar_weight_order(N)[::-1]
c=json.load(open('workspace/r2_binary_baseline_shg_64/construction_frozen_G2.json'))
gp=[g for g in c['grid_points'] if g['sc_margin']==0.02][0]
T=400
for li in (3,5,6,7,8,9):
    L=gp['layers'][li];p=L['ber'];k=L['k'];info=np.sort(order[:k]);mask=np.zeros(N,np.uint8);mask[info]=1
    s=l=0
    for t in range(T):
        a=rng.integers(0,2,N).astype(np.int8);ua=enc(a,nl);b=a^(rng.random(N)<p).astype(np.int8)
        lam=math.log((1-p)/p);llr=np.where(b==0,lam,-lam)
        uh=scd(llr,mask.astype(np.int8),ua,nl);s+=int(not np.array_equal(uh[info],ua[info]))
        o=dec.decode_batch_frozen(N,k,1,mask,(ua*(1-mask)).astype(np.uint8).reshape(1,N),llr.astype(np.float32).reshape(1,N))[0]
        l+=int(not np.array_equal(o,ua[info]))
    print('layer',li,'p',p,'k',k,'cal',L['fer_calibrated'],'SC fail',s/T,'SCL(frozen-fixed,no CRC) fail',l/T,flush=True)
