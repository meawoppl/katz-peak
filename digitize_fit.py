import numpy as np
from PIL import Image
from scipy.optimize import curve_fit

im = np.asarray(Image.open("data/ballmer_xkcd323.png").convert("RGB")).astype(int)
r, g, b = im[..., 0], im[..., 1], im[..., 2]
red = (r > 180) & (g < 120) & (b < 120)
red[300:] = False

X0, PX_PER_UNIT, Y0 = 153.0, 1438.5, 257.0
cols = np.unique(np.nonzero(red)[1])
bac, skill = [], []
for c in cols:
    ys = np.nonzero(red[:, c])[0]
    bac.append((c - X0) / PX_PER_UNIT)
    skill.append(Y0 - ys.min() - 1.0)
bac, skill = np.array(bac), np.array(skill)
sober = skill[:3].mean()
skill /= sober

def model(b, A, tau, p, H, b0, gam, eps):
    judgement = A * np.exp(-(b / tau) ** p)
    resonance = H * gam**2 / ((b - b0) ** 2 + gam**2)
    return judgement + resonance + eps

p0 = [1.0, 0.07, 1.5, 2.0, 0.134, 0.002, 0.0]
lo = [0.5, 0.01, 0.5, 0.5, 0.12, 0.0003, -0.2]
hi = [1.5, 0.3, 6.0, 5.0, 0.15, 0.02, 0.2]
popt, pcov = curve_fit(model, bac, skill, p0=p0, bounds=(lo, hi), maxfev=200000)
perr = np.sqrt(np.diag(pcov))
res = skill - model(bac, *popt)
r2 = 1 - (res**2).sum() / ((skill - skill.mean()) ** 2).sum()
names = ["A", "tau", "p", "H", "b0", "gam", "eps"]
for n, v, e in zip(names, popt, perr):
    print(f"{n:4s} = {v:.5f} +/- {e:.5f}")
print("R2", r2, "N", len(bac), "rms", np.sqrt((res**2).mean()))
np.savez("fit.npz", bac=bac, skill=skill, popt=popt, perr=perr, r2=r2)
