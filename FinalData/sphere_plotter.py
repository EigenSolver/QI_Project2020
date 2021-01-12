import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
import sys


# truncates the colormap to a certain range of colors, snippet taken from stackoverflow
def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap


# file path for the input data
file_path = sys.argv[1]
# title on the picture
title = sys.argv[2]

# Read coordinates and fideilities for the two copies
theta, phi, p0_1, p0_2 = np.loadtxt(file_path, delimiter="\t", usecols=(0, 1, 2, 4), unpack=True)

# Remove the ".txt" extension of the input file
file_path = file_path[:-4]  # remove the last four characters of the path

# modify phi so that it belongs to [-pi,pi], but keep phi=0 fixed (longitude goes from -180 to +180)
for i in range(len(phi)):
    if phi[i] >= np.pi:
        phi[i] = -np.pi + phi[i] % np.pi

colormap = plt.get_cmap('plasma')

# Only keep the darker colors, so we can use white for the central labels
new_colormap = truncate_colormap(colormap, 0, 0.9)

# Plot the fidelity for the first copy using the Mollweide projection of the sphere
fig1 = plt.figure(1)
ax1 = fig1.add_subplot(111, projection="mollweide")
ax1.grid(True)
ax1.tick_params(axis='x', colors='white')
sc1 = ax1.scatter(phi, np.pi / 2 - theta, c=p0_1, lw=5, s=155, alpha=1, cmap=new_colormap)
cbar1 = plt.colorbar(sc1, orientation="horizontal")
cbar1.set_label('Fidelity')
plt.title(title + "\nCopy 1\n")
fig1.savefig(file_path + "_copy1.png", dpi=300)

# Plot the fidelity for the second copy using the Mollweide projection of the sphere
fig2 = plt.figure(2)
ax2 = fig2.add_subplot(111, projection="mollweide")
ax2.grid(True)
ax2.tick_params(axis='x', colors='white')
sc2 = ax2.scatter(phi, np.pi / 2 - theta, c=p0_2, lw=5, s=155, alpha=1, cmap=new_colormap)
cbar2 = plt.colorbar(sc2, orientation="horizontal")
cbar2.set_label('Fidelity')
plt.title(title + "\nCopy 2\n")
fig2.savefig(file_path + "_copy2.png", dpi=300)
