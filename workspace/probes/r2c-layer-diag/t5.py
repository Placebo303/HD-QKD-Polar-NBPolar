from common import *
from genie import *
layer=8; nl=8; n=1<<nl
root=m.de_root_llr(tables,PM,layer,d,layers,m_root=200000,seed=1)
pop=lab.de.de_llr_populations_from_root(root,nl,n_samples=20000,seed=2)
zde=np.mean(np.exp(-np.abs(pop)/2),1); zde_s=np.mean(np.exp(-np.clip(pop,-700,700)/2),1); pe_de=(pop<0).mean(1)
rng=np.random.default_rng(3); F=20000
a,b,x,llr=draw_layer(rng,layer,F*n); x=x.reshape(F,n); llr=llr.reshape(F,n)
u=np.stack([m.encode(lab,xi,nl) for xi in x])
Z,E,S=genie_sc_stats(llr,u,f_ex); Zm=Z/F; Em=E/F
print("idx  Zde  Zde_signed  Zmc(exact f) | Pe_de Pe_mc")
for i in [0,1,2,3,7,15,31,63,127,128,191,200,223,239,247,251,253,254,255]:
    print(i,f"{zde[i]:.4f} {zde_s[i]:.4f} {Zm[i]:.4f} | {pe_de[i]:.4f} {Em[i]:.4f}")
print("corr log Z", np.corrcoef(np.log(zde+1e-12),np.log(Zm+1e-12))[0,1])
