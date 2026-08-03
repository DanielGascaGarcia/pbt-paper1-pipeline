#Code: 6.Simulation.py
#Description: Simulation of Blood Glucose given the Bolus insulin infused.
#Created 15th November 2022
#Author: mbaxdg6

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