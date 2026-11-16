import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = np.load("fit.npz")
bac, skill, popt, r2 = d["bac"], d["skill"], d["popt"], float(d["r2"])
A, tau, p, H, b0, gam, eps = popt

plt.rcParams.update({
    "font.family": "serif", "font.size": 9, "axes.linewidth": 0.8,
    "mathtext.fontset": "cm", "savefig.bbox": "tight", "savefig.dpi": 300,
})

def kww(b, t):
    return np.exp(-(b / t) ** p)

def lorentz(b, h, c, g):
    return h * g**2 / ((b - c) ** 2 + g**2)

def ballmer(b):
    return A * kww(b, tau) + lorentz(b, H, b0, gam) + eps

TAU_M = 0.10
TAU_J = (tau ** -p - TAU_M ** -p) ** (-1 / p)
B_C, W_C = 0.30, 0.012
LAM_J, LAM_M, LAM_K, LAM_0 = 0.35, 0.80, 1.45, 0.55

def consciousness(b):
    return 1 / (1 + np.exp((b - B_C) / W_C))

def katz(b):
    J, M = kww(b, TAU_J), kww(b, TAU_M)
    J2, M2 = J + LAM_J * (1 - J), M + LAM_M * (1 - M)
    s = np.sqrt(1 + LAM_K)
    peak = lorentz(b, H * (1 + LAM_J) * s, b0 * s, gam * s)
    return (A * (1 + LAM_0) * J2 * M2 + peak + eps) * consciousness(b)

b = np.linspace(0, 0.36, 8000)

# Figure 1: data + fit + residuals
fig, (ax, axr) = plt.subplots(2, 1, figsize=(5.2, 3.9), sharex=True,
                              gridspec_kw={"height_ratios": [3, 1], "hspace": 0.06})
ax.plot(bac, skill, "o", ms=1.8, mfc="none", mec="0.35", mew=0.5, label="Munroe (2008), digitized")
ax.plot(b[b < 0.275], ballmer(b[b < 0.275]), "-", c="#b2182b", lw=1.0, label="Eq. (1), best fit")
ax.set_ylabel(r"Programming skill $S/S_0$")
ax.legend(frameon=False, loc="upper right")
ax.set_ylim(-0.1, 2.75)
ins = ax.inset_axes([0.52, 0.22, 0.25, 0.40])
m = (bac > 0.125) & (bac < 0.145)
bb = np.linspace(0.125, 0.145, 800)
ins.plot(bac[m], skill[m], "o", ms=1.8, mfc="none", mec="0.35", mew=0.5)
ins.plot(bb, ballmer(bb), "-", c="#b2182b", lw=1.0)
ins.axvspan(b0 - gam, b0 + gam, color="#b2182b", alpha=0.12, lw=0)
ins.tick_params(labelsize=6)
ins.set_title(r"$b_0 \pm \gamma$", fontsize=7)
res = skill - ballmer(bac)
axr.axhline(0, c="0.6", lw=0.6)
axr.plot(bac, res, "o", ms=1.5, mfc="none", mec="0.35", mew=0.5)
axr.set_ylabel("Resid.")
axr.set_xlabel("Blood alcohol concentration $b$ (%)")
axr.set_xlim(0, 0.28)
fig.savefig("fig1_fit.pdf")

# Figure 2: mechanistic decomposition
fig, ax = plt.subplots(figsize=(5.2, 2.9))
bb = b[b < 0.32]
ax.plot(bb, kww(bb, TAU_J), c="#2166ac", lw=1.0, label=r"Judgement $\mathcal{J}(b)$")
ax.plot(bb, kww(bb, TAU_M), c="#4dac26", lw=1.0, ls="--", label=r"Motor fidelity $\mathcal{M}(b)$")
ax.plot(bb, consciousness(bb), c="0.3", lw=1.0, ls=":", label=r"Consciousness $\mathcal{C}(b)$")
ax.plot(bb, A * kww(bb, tau), c="#5e3c99", lw=1.6, alpha=0.6, label=r"Impairment envelope $A\,\mathcal{J}\mathcal{M}$")
ax2 = ax.twinx()
ax2.plot(bb, lorentz(bb, H, b0, gam), c="#b2182b", lw=1.0, label=r"Disinhibition resonance $\mathcal{D}(b)$")
ax2.set_ylabel(r"$\mathcal{D}(b)$", color="#b2182b")
ax2.tick_params(axis="y", colors="#b2182b")
ax.set_xlabel("Blood alcohol concentration $b$ (%)")
ax.set_ylabel("Normalized faculty")
ax.set_xlim(0, 0.32)
ax.set_ylim(0, 1.05)
ax2.set_ylim(0, 2.8)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, frameon=False, fontsize=7, loc="center right", bbox_to_anchor=(0.97, 0.62))
fig.savefig("fig2_decomposition.pdf")

# Figure 3: Widmark dwell time
BETA = 0.015
t = np.linspace(0, 10, 4000)
bt = np.clip(0.20 - BETA * t, 0, None)
fig, ax = plt.subplots(figsize=(5.2, 2.4))
ax.plot(t, ballmer(bt), c="#b2182b", lw=1.0)
ax.set_xlabel("Time since loading dose $t$ (h)")
ax.set_ylabel(r"$S/S_0$")
t_in = (0.20 - b0) / BETA
ax.axvspan(t_in - gam / BETA, t_in + gam / BETA, color="#b2182b", alpha=0.15, lw=0)
ax.annotate(f"Productive window\n{2 * gam / BETA * 60:.0f} min", xy=(t_in, 2.3),
            xytext=(t_in + 1.6, 1.9), fontsize=7, arrowprops=dict(arrowstyle="->", lw=0.6))
ax.set_xlim(0, 10)
fig.savefig("fig3_widmark.pdf")

# Figure 4: the Katz shift
fig, ax = plt.subplots(figsize=(5.2, 3.2))
ax.plot(b, ballmer(b), c="0.55", lw=1.0, ls="--", label="Unassisted (Ballmer regime)")
ax.plot(b, katz(b), c="#b2182b", lw=1.2, label="LLM-assisted (Katz regime)")
bk = b0 * np.sqrt(1 + LAM_K)
ax.annotate("Ballmer Peak\n(deprecated)", xy=(b0, ballmer(b0)), xytext=(0.03, 3.1),
            fontsize=7, arrowprops=dict(arrowstyle="->", lw=0.6, color="0.4"), color="0.35")
ax.annotate("Katz Peak", xy=(bk + 0.002, 5.0), xytext=(bk + 0.03, 4.4),
            fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.6))
ax.annotate("Loss of $\\mathcal{C}$\n(LLM cannot help)", xy=(0.30, katz(0.30)), xytext=(0.262, 1.35),
            fontsize=6.5, color="0.35", arrowprops=dict(arrowstyle="->", lw=0.5, color="0.4"))
ax.annotate("", xy=(bk - 0.012, 1.6), xytext=(b0 + 0.006, 1.6),
            arrowprops=dict(arrowstyle="->", lw=0.8, color="#2166ac"))
ax.text((b0 + bk) / 2 - 0.003, 1.7, r"$\Delta b$", ha="center", fontsize=8, color="#2166ac")
ax.annotate("", xy=(0.004, katz(0.0)), xytext=(0.004, ballmer(0.0)),
            arrowprops=dict(arrowstyle="<->", lw=0.6, color="#2166ac", shrinkA=0, shrinkB=0))
ax.text(0.008, 1.22, r"$1+\lambda_0$", fontsize=7, color="#2166ac", va="center")
ax.axvline(0.08, c="0.75", lw=0.6, ls=":")
ax.text(0.082, 4.3, "U.S. legal driving limit\n(not a coding limit)", fontsize=6, color="0.45", va="top")
ax.set_xlabel("Blood alcohol concentration $b$ (%)")
ax.set_ylabel(r"Programming skill $S/S_0$")
ax.set_xlim(0, 0.36)
ax.set_ylim(0, 6.6)
ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.99), fontsize=7)
fig.savefig("fig4_katz_shift.pdf")
fig.savefig("fig4_katz_shift.png", dpi=150)

# Numbers for the text
bk = b0 * np.sqrt(1 + LAM_K)
bgrid = np.linspace(0.18, 0.25, 200000)
kpk = bgrid[np.argmax(katz(bgrid))]
print(f"TAU_J={TAU_J:.4f}  TAU_M={TAU_M}")
print(f"b0={b0:.4f} gam={gam:.5f} Q={b0/(2*gam):.1f} H={H:.3f} S(b0)={ballmer(b0):.3f}")
print(f"katz peak b={kpk:.4f} S={katz(kpk):.3f} gam'={gam*np.sqrt(1+LAM_K):.5f}")
print(f"excess skill integral = {np.pi*H*gam:.4f}")
print(f"dwell ballmer = {2*gam/BETA*60:.1f} min, katz = {2*gam*np.sqrt(1+LAM_K)/BETA*60:.1f} min")
for bv, gv, lab in [(b0, gam, "ballmer"), (kpk, gam * np.sqrt(1 + LAM_K), "katz")]:
    g = bv / 100 * 0.68 * 80000
    tol = gv / 100 * 0.68 * 80000
    print(f"{lab}: ethanol {g:.1f} g = {g/14:.2f} std drinks; maint {BETA/100*0.68*80000:.2f} g/h = {BETA/100*0.68*80000/14:.2f} drinks/h; precision +/- {tol:.2f} g = {tol/0.789/0.4:.1f} mL of 40% ABV")
pre = (b > 0.14) & (b < 0.2)
print(f"katz approach min {katz(b[pre]).min():.4f} at {b[pre][np.argmin(katz(b[pre]))]:.4f}")
drinks = kpk / 100 * 0.68 * 80000 / 14 + 8 * BETA / 100 * 0.68 * 80000 / 14
print(f"drinks/day {drinks:.3f} cost {drinks*1.5:.2f} incr {(katz(kpk)-1)*800:.2f} ratio {(katz(kpk)-1)*800/(drinks*1.5):.1f}")
print(f"S(0) fitted {ballmer(0.0):.4f}; C at last datum {consciousness(bac.max()):.3f}; bac range {bac.min():.6f}-{bac.max():.6f}")
print(f"S at 0.08 ballmer {ballmer(0.08):.3f}; katz sober {katz(0.0):.3f}; ballmer sober {ballmer(0.0):.3f}")
