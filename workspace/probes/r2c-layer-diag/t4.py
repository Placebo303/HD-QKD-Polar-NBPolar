from common import *
layer=8
root=m.de_root_llr(tables,PM,layer,d,layers,m_root=4096,seed=m.ROOT_SEED_BASE+layer)
rng=np.random.default_rng(m.DE_SEED); mm=1024
pop=root[rng.integers(0,root.size,size=(1,mm))]
idx=16727; bits=[(idx>>(14-j))&1 for j in range(15)]
print("path bits (0=f,1=g):",bits)
print("level0 frac>20", (np.abs(pop)>20).mean(), "neg", (pop<0).mean())
de=lab.de
for lvl in range(15):
    nodes=pop.shape[0]
    pa=rng.integers(0,mm,size=(nodes,mm)); pb=rng.integers(0,mm,size=(nodes,mm)); rows=np.arange(nodes)[:,None]
    l1=pop[rows,pa]; l2=pop[rows,pb]
    cf=de._boxplus(l1,l2,40.0); cg=np.clip(l1+l2,-40.0,40.0)
    out=np.empty((2*nodes,mm)); out[0::2]=cf; out[1::2]=cg; pop=out
    # track node on the path: prefix of idx
    r=idx>>(14-lvl)
    print(lvl,"bit",bits[lvl],"node",r,"frac>20",round((pop[r]>20).mean(),4),"neg",round((pop[r]<0).mean(),4),"min",round(pop[r].min(),2))
    if pop.shape[0] > 2**14: pass
