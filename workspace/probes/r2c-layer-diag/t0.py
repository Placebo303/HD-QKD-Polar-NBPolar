from common import *
print("H_delta true", H_DELTA, "model sum", PM.sum())
print("caps model", np.round(ch["caps"],4), ch["sum_caps"])
print("stage", run.STAGE)
dec = dec_new(); rng = np.random.default_rng(1)
order = m.de_order(lab, tables, PM, 9, d, layers, NLOG, root_seed=5)
a,b,x,llr = draw_layer(rng, 9, N*4)
x=x.reshape(4,N); llr=llr.reshape(4,N)
t=time.time(); e=fer_scl(dec, order, 10000, x, llr); print("scl 4 frames", time.time()-t, e)
