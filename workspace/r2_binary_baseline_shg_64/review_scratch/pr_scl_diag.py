import sys,math,time
sys.path.insert(0,'.')
import numpy as np
from src.reconciliation.real_polar_sc_rescue import polar_encode_non_systematic as enc, polar_sc_decode_with_frozen as scd, _polar_weight_order
from src.reconciliation.cpp_scl_wrapper import PolarSCLDecoder
from experiments.run_real_polar_max_pie import calc_crc16
N=4096;nl=12;rng=np.random.default_rng(1)
dec=PolarSCLDecoder()
print(dec.lib_path)
order=_polar_weight_order(N)[::-1]
def llr_of(b,p):
    lam=math.log((1-p)/p);return np.where(b==0,lam,-lam)
def trial(p,k,mode):
    info=np.sort(order[:k]);mask=np.zeros(N,np.uint8);mask[info]=1
    e=(rng.random(N)<p).astype(np.int8)
    if mode=='msgcode': # channel-coding: frozen=0, CRC embedded
        u=np.zeros(N,np.int8);msg=rng.integers(0,2,k-16).astype(np.int8)
        u[info[:k-16]]=msg;u[info[k-16:]]=np.asarray(calc_crc16(msg),np.int8)
        x=enc(u,nl);b=x^e
        out=dec.decode_batch(N,k,1,mask,llr_of(b,p).astype(np.float32).reshape(1,N))[0]
        return np.array_equal(out[:k-16],msg)
    a=rng.integers(0,2,N).astype(np.int8);ua=enc(a,nl);b=a^e
    if mode=='runpy': # what run.py does
        out=dec.decode_batch(N,k,1,mask,llr_of(b,p).astype(np.float32).reshape(1,N))[0]
        return np.array_equal(out[:k-16],ua[info[:k-16]])
    if mode=='frozen_genie_noCRCfix': # frozen genie values, CRC slot = real data (CRC check will just fail->fallback best pm)
        out=dec.decode_batch_frozen(N,k,1,mask,(ua*(1-mask)).astype(np.uint8).reshape(1,N),llr_of(b,p).astype(np.float32).reshape(1,N))[0]
        return np.array_equal(out[:k-16],ua[info[:k-16]])
    if mode=='frozen_genie_fullexact':
        out=dec.decode_batch_frozen(N,k,1,mask,(ua*(1-mask)).astype(np.uint8).reshape(1,N),llr_of(b,p).astype(np.float32).reshape(1,N))[0]
        return np.array_equal(out,ua[info])
    if mode=='sc':
        m=mask.astype(np.int8);uh=scd(llr_of(b,p),m,ua,nl);return np.array_equal(uh,ua)
p,k=0.0157,2828
for mode in ('msgcode','runpy','frozen_genie_noCRCfix','frozen_genie_fullexact','sc'):
    t=time.time();n=12 if mode!='sc' else 6
    r=[trial(p,k,mode) for _ in range(n)];print(mode,sum(r),'/',n,round(time.time()-t,1),'s',flush=True)
