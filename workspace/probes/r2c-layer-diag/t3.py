from common import *
import genie
sys.setrecursionlimit(10000)
layer=8; idxs=[16727,16943,16702]
def genie_capture(llr,u,fnode,idxs):
    cap={i:None for i in idxs}
    def rec(al,us,off):
        n=al.shape[1]
        if n==1:
            if off in cap: cap[off]=(al[:,0]*(1-2.0*us[:,0])).copy()
            return us.astype(np.int8)
        h=n//2; l,r=al[:,:h],al[:,h:]
        bl=rec(fnode(l,r),us[:,:h],off); br=rec(r+(1-2.0*bl)*l,us[:,h:],off+h)
        return np.concatenate([bl^br,br],axis=1)
    rec(llr.astype(np.float64),u.astype(np.int8),0); return cap
rng=np.random.default_rng(11)
a,b,x,llr=draw_layer(rng,layer,256*N); x=x.reshape(256,N); llr=llr.reshape(256,N)
u=np.stack([m.encode(lab,xi,NLOG) for xi in x])
for nm,fn in (("ms",genie.f_ms),("ex",genie.f_ex)):
    cp=genie_capture(llr,u,fn,idxs)
    for i in idxs: s=cp[i]; print(nm,i,"quantiles",np.round(np.quantile(s,[0,.05,.25,.5,.75,1]),2),"Pe",(s<0).mean())
root=m.de_root_llr(tables,PM,layer,d,layers,m_root=4096,seed=m.ROOT_SEED_BASE+layer)
pop=lab.de.de_llr_populations_from_root(root,NLOG,n_samples=1024,seed=m.DE_SEED)
for i in idxs: print("DE",i,np.round(np.quantile(pop[i],[0,.05,.25,.5,.75,1]),2))
