import json, glob
r = {"prereg": "prereg.md", "channel": "true pmf 0:.83,+-1:.085,floor 1e-9 (tail mass 1.02e-6), H=0.8277 bit; model = m2_pmf floor 1e-15; d=1024,N=32768,clip30,L=16 (min-sum SCL, native)"}
r["A_C_exact"] = json.load(open("partA_C.json"))
r["B_layer8_9_constructions_128frames"] = {l: json.load(open(f"partB_L{l}.json")) for l in (8, 9)}
r["B2_DE1024_vs_MC4096_fer_by_layer_mu"] = {l: json.load(open(f"partB2_L{l}.json")) for l in range(10)}
r["G_DE2400_and_freshMC_sumPe"] = {l: json.load(open(f"partG_L{l}.json")) for l in (5, 8, 9)}
r["D_block_path_true_vs_decoded_prefix"] = json.load(open("partD.json"))
r["E_decoder"] = {l: json.load(open(f"partE_L{l}.json")) for l in (7, 8, 9)}
r["F_single_confident_wrong_symbol"] = [json.load(open(f)) for f in sorted(glob.glob("partF_*.json"))]
json.dump(r, open("results.json", "w"), indent=1)
