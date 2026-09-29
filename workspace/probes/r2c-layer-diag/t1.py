from common import *
from genie import *
# sanity: BSC-like small check of ordering vs polar 2^4
rng=np.random.default_rng(3)
a,b,x,llr = draw_layer(rng, 9, 200*N)
x=x.reshape(200,N); llr=llr.reshape(200,N)
u=np.stack([m.encode(lab,xi,NLOG) for xi in x])
t=time.time(); Z,E,S=genie_sc_stats(llr,u); print("genie 200 frames", time.time()-t)
print(Z[:5]/200, E[-5:]/200)
