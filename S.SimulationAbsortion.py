"""
S.SimulationAbsortion.py   (header of the original file reads "6.Simulation.py")
Figure 5 of paper 1: Rayleigh densities with peaks at 1, 2, 4 and 8 hours.

Created: 15 November 2022
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    Plots the probability density of four Rayleigh distributions (scale 1, 2,
    4 and 8 h) over 0-12 h. The peak of a Rayleigh density is at its scale,
    so the curves peak at 1, 2, 4 and 8 h. The curve with scale 1 h is the
    one used for rapid-acting insulin in 6.SimulationBasalAutomated.py.
    (The original header described a blood glucose simulation from boluses;
    that is not what this script does.)

Inputs
    globals.path3, globals.FIGURE_TITLES   (no data files)

Output
    <path3>/Figure5.png
"""

# globals is imported first: it selects the non-interactive backend, which
# has to happen before pyplot/pylab is loaded.
import globals

from scipy.stats import rayleigh
import numpy as np
import pylab as pl
import matplotlib
import os

matplotlib.rcParams.update({'font.size': 12})
pl.figure(figsize=(10, 6));

path3 = globals.path3;
os.makedirs(path3, exist_ok=True);


# 144 time points over 0-12 h (about one every 5 minutes).
# rayleigh(loc, scale): loc = 0, scale = time of the peak in hours.
#Rapid
x=np.linspace(0,12,144);
a, b = 0, 1;
dist1=rayleigh(a, b);
a, b = 0, 2;
dist2=rayleigh(a, b);
a, b = 0, 4;
dist3=rayleigh(a, b)
a, b = 0, 8;
dist4=rayleigh(a, b)


pl.plot(x,dist1.pdf(x), 'o',label='Peak at 1 h');
pl.plot(x,dist2.pdf(x), 'o',label='Peak at 2 h');
pl.plot(x,dist3.pdf(x), 'o',label='Peak at 4 h');
pl.plot(x,dist4.pdf(x), 'o',label='Peak at 8 h');
pl.legend();
pl.ylabel("Probability density");
pl.xlabel("Time (h)");

# The journal puts the figure title in the caption, not inside the image.
# globals.FIGURE_TITLES has to be read explicitly: importing globals does
# not apply it on its own.
if globals.FIGURE_TITLES:
    pl.title("PDF of Rayleigh distribution with peaks at different times.");

pl.grid();
pl.savefig(path3 + 'Figure5.png', dpi=300, bbox_inches='tight');
print("Saved:", os.path.abspath(path3 + 'Figure5.png'));
pl.close();