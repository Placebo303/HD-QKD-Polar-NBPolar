from common import *
J = joint(PT); JM = joint(PM)
capT = lab.msd.conditional_capacities(J, d)["conditional_mi_bits"]
capM = lab.msd.conditional_capacities(JM, d)["conditional_mi_bits"]
res = {"H_delta_true": H_DELTA, "caps_lab_on_true_pmf": capT, "caps_impl(model pmf, floor1e-15)": list(ch["caps"])}
mu = 0.084
rows = []
for i in range(layers):
    blk = d >> (i+1)
    P = J.reshape(2**(i+1), blk, d).sum(1).reshape(2**i, 2, d)     # P[pref,x,b]
    Pb = P.sum(1)                                                  # P[pref,b]
    with np.errstate(divide="ignore", invalid="ignore"):
        q = P / np.maximum(Pb[:, None, :], 1e-300)
        Hc = -(P * np.log2(np.maximum(q, 1e-300))).sum()
    cap_direct = 1 - Hc          # a_i uniform indep of prefix -> H(a_i)=1
    L = tables.llr[i]            # model LLR (clipped)
    Ltrue = np.log(np.maximum(P[:, 0, :], 1e-300) / np.maximum(P[:, 1, :], 1e-300))
    # decoder-view GMI (bits): 1 - E log2(1+exp(-s L)), s=+1 for x=0, -1 for x=1
    gmi = 1 - (P[:, 0, :] * np.logaddexp(0, -L) + P[:, 1, :] * np.logaddexp(0, L)).sum() / np.log(2)
    # sign errors
    perr_model = (P[:, 1, :] * (L > 0) + P[:, 0, :] * (L < 0) + 0.5 * (P[:, 0, :] + P[:, 1, :]) * (L == 0)).sum()
    perr_bayes = np.minimum(P[:, 0, :], P[:, 1, :]).sum()
    aL = np.abs(L)
    tot = P.sum(1)
    wrong = np.where(L > 0, P[:, 1, :], np.where(L < 0, P[:, 0, :], 0.5 * tot))
    bins = [0, 0.5, 1, 2, 3, 5, 10, 20, 29.99, 31]
    cal = []
    for lo, hi in zip(bins[:-1], bins[1:]):
        sel = (aL >= lo) & (aL < hi)
        mass = tot[sel].sum()
        if mass > 0:
            emp = wrong[sel].sum() / mass
            pred = (tot[sel] / (1 + np.exp(aL[sel]))).sum() / mass
            cal.append({"absL": [lo, hi], "mass": float(mass), "err_emp": float(emp), "err_pred": float(pred), "wrong_mass": float(wrong[sel].sum())})
    sel = aL > 10
    conf_wrong = float(wrong[sel].sum())
    conf_wrong_true = float(wrong[aL >= 29.99].sum())
    # frame-level: expected # confident-wrong symbols per N=32768 codeword
    diffL = np.abs(np.clip(Ltrue, -30, 30) - L)
    k = int(np.floor(N * max(0.0, capM[i] - mu))) if False else int(np.floor(N * max(0.0, ch["caps"][i] - mu)))
    rows.append({"layer": i, "cap_lab_true": capT[i], "cap_direct_exact": float(cap_direct), "cap_lab_model": capM[i], "cap_impl": float(ch["caps"][i]),
        "H_i_exact": float(1 - cap_direct), "GMI_decoder_view_bits": float(gmi), "GMI_loss_vs_cap": float(cap_direct - gmi),
        "k_at_mu_0.084": k, "k_over_N": k / N, "N(1-H_i)": N * cap_direct, "rate_over_cap": k / (N * cap_direct),
        "sign_err_model": float(perr_model), "sign_err_bayes": float(perr_bayes),
        "conf_wrong_prob_absL>10": conf_wrong, "expected_conf_wrong_per_codeword(N=32768)": conf_wrong * N,
        "clipped_mass": float(tot[aL >= 29.99].sum()), "wrong_at_clip_prob": conf_wrong_true, "expected_wrong_at_clip_per_cw": conf_wrong_true * N,
        "mean_absL_true_vs_model_maxdiff": float(diffL.max()), "calibration": cal})
res["layers"] = rows
json.dump(res, open(OUT + "/partA_C.json", "w"), indent=1)
print("H_i exact:", [round(r["H_i_exact"], 5) for r in rows], "sum", sum(r["H_i_exact"] for r in rows))
for r in rows:
    print(r["layer"], "cap", round(r["cap_direct_exact"], 4), "impl", round(r["cap_impl"], 4), "GMIloss", round(r["GMI_loss_vs_cap"], 5), "k/N", round(r["k_over_N"], 3),
          "perr", round(r["sign_err_model"], 4), "bayes", round(r["sign_err_bayes"], 4), "confwrong/cw", round(r["expected_conf_wrong_per_codeword(N=32768)"], 3),
          "clipmass", round(r["clipped_mass"], 4), "wrongAtClip/cw", round(r["expected_wrong_at_clip_per_cw"], 4))
for r in rows[7:]:
    print("layer", r["layer"]); [print("  ", c) for c in r["calibration"]]
