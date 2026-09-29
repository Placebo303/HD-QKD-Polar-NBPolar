from common import *
from genie import *
layer=8; k0=23141
O=np.load(f"{OUT}/orders_L{layer}.npy")  # rows: DE1024_impl, alt, DE4096, ...
rng=np.random.default_rng(2); Zt=np.zeros(N);Et=np.zeros(N)
for c in range(16):
    a,b,x,llr=draw_layer(rng,layer,256*N); x=x.reshape(256,N); llr=llr.reshape(256,N)
    u=np.stack([m.encode(lab,xi,NLOG) for xi in x]); Z,E,S=genie_sc_stats(llr,u,f_ms); Zt+=Z;Et+=E
Zt/=4096;Et/=4096
o=O[0]; inf=o[:k0]; bad=inf[np.argsort(-Et[inf])[:15]]
print("bad included idx", bad, "Pe", np.round(Et[bad],3), "Zmc", np.round(Zt[bad],3))
rank=np.empty(N,int); rank[o]=np.arange(N); print("DE rank of bad", rank[bad])
print("popcount", [bin(i).count('1') for i in bad], "worst-pos idx by MC:", np.argsort(-Et)[:8])
# rerun DE1024 impl and print Z of bad
root = m.de_root_llr(tables, PM, layer, d, layers, m_root=4096, seed=m.ROOT_SEED_BASE + layer)
pop = lab.de.de_llr_populations_from_root(root, NLOG, n_samples=1024, seed=m.DE_SEED)
z=np.mean(np.exp(-np.abs(pop)/2),axis=1)
print("DE z of bad", z[bad], "pop min/max at bad", [ (pop[i].min(), pop[i].max(), (pop[i]<0).mean()) for i in bad[:6]])
print("root stats: frac |root|>=29.9", (np.abs(root)>29.9).mean(), "frac<0", (root<0).mean(), "mean", root.mean())
