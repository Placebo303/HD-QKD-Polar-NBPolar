import sys,math
sys.path.insert(0,'.')
import numpy as np
from src.reconciliation.real_polar_sc_rescue import polar_encode_non_systematic as enc, polar_sc_decode_with_frozen as scd, polar_sc_decode as sc0,_polar_weight_order
N=4096;nl=12;rng=np.random.default_rng(1)
order=_polar_weight_order(N)[::-1]
def run(p,k,mode,T=20):
    info=order[:k];mask=np.zeros(N,np.int8);mask[info]=1;ok=0
    for t in range(T):
        e=(rng.random(N)<p).astype(np.int8)
        if mode=='calib0':   # frozen=0, random info (baseline's calibration)
            u=np.zeros(N,np.int8);u[info]=rng.integers(0,2,k);x=enc(u,nl);b=x^e
        else:                # source-coding: a random, u=enc(a) genie frozen
            a=rng.integers(0,2,N).astype(np.int8);u=enc(a,nl);x=a;b=a^e
        lam=math.log((1-p)/p);llr=np.clip(np.where(b==0,lam,-lam),-20,20)
        fz=u if mode!='calib0' else np.zeros(N,np.int8)
        uh=scd(llr,mask,fz.astype(np.int8),nl);ok+=int(np.array_equal(uh[info],u[info]))
    return ok
for p,k in ((0.0157,2828),(0.0157,1500),(0.0005,3789)):
    print(p,k,'calib0',run(p,k,'calib0'),'srcgenie',run(p,k,'src'),flush=True)
# check involution and e=0
a=rng.integers(0,2,N).astype(np.int8);print('invol',np.array_equal(enc(enc(a,nl),nl),a))
