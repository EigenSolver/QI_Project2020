import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
import sys

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap


file_path = sys.argv[1]
title = sys.argv[2]

theta, phi, p0_1, p0_2 = np.loadtxt(file_path, delimiter="\t", usecols=(0, 1, 2, 4), unpack=True)

colormap = plt.get_cmap('plasma')
new_colormap = truncate_colormap(colormap, 0, 0.9)

fig1 = plt.figure(1)
ax1 = fig1.add_subplot(111, projection="mollweide")
ax1.grid(True)
ax1.tick_params(axis='x', colors='white')
sc1 = ax1.scatter(phi-np.pi, theta-np.pi/2, c=p0_1,lw=5, s=150,alpha=1,cmap=new_colormap)
#sc1 = ax1.scatter(phi-np.pi, theta-np.pi/2, c=p0_1,lw=0, s=50,alpha=1,cmap=new_colormap)
cbar1 = plt.colorbar(sc1,orientation="horizontal")
cbar1.set_label('Fidelity')
plt.title(title+"\nCopy 1\n")
fig1.savefig(file_path+"_copy1.png", dpi=300)

fig2 = plt.figure(2)
ax2 = fig2.add_subplot(111, projection="mollweide")
ax2.grid(True)
ax2.tick_params(axis='x', colors='white')
sc2 = ax2.scatter(phi-np.pi, theta-np.pi/2, c=p0_2,lw=5, s=150,alpha=1,cmap=new_colormap)
#sc2 = ax2.scatter(phi-np.pi, theta-np.pi/2, c=p0_2,lw=0, s=50,alpha=1,cmap=new_colormap)
cbar2 = plt.colorbar(sc2,orientation="horizontal")
cbar2.set_label('Fidelity')
plt.title(title+"\nCopy 2\n")
fig2.savefig(file_path+"_copy2.png", dpi=300)

plt.show()