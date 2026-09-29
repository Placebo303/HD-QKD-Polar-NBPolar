import sys,math
sys.path.insert(0,'.')
import numpy as np
from src.reconciliation.real_polar_sc_rescue import polar_encode_non_systematic as enc, polar_sc_decode_with_frozen as scd, _polar_weight_order
N=4096;nl=12;rng=np.random.default_rng(1)
order=_polar_weight_order(N)[::-1]
for p,k in ((0.0005,3789),(0.0157,2828),(0.0157,2300),(0.0157,1500),(0.1245,1255),(0.2438,439)):
    info=order[:k];mask=np.zeros(N,np.int8);mask[info]=1
    ok=0;bl=[]
    for t in range(20):
        a=rng.integers(0,2,N).astype(np.int8);ua=enc(a,nl);e=(rng.random(N)<p).astype(np.int8);b=a^e
        lam=math.log((1-p)/p);llr=np.clip(np.where(b==0,lam,-lam),-20,20)
        uh=scd(llr,mask,ua,nl);ok+=int(np.array_equal(enc(uh,nl),a))
    print(p,k,ok,'/20',flush=True)
