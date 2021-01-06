import os

import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
from matplotlib import colors
import matplotlib.pyplot as plt

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

def phase_covariant_fidelity(theta,phi):
    return (3*(4-np.sqrt(2))+(3*np.sqrt(2)-4)*(np.cos(2*phi)+np.cos(2*theta)*(1-np.cos(2*phi))))/(16*(2-np.sqrt(2)))

#This is for xy equator. needs to be corrected
def economical_phase_covariant_fidelity(theta,phi):
    return 1/8*(2*np.cos(theta)-(np.sqrt(2)-1)*np.cos(2*theta)+np.sqrt(2)+5)

theta = np.linspace(0, np.pi, 300)
phi = np.linspace(0, 2*np.pi, 300)

theta, phi = np.meshgrid(theta, phi)
p0_1_ideal = economical_phase_covariant_fidelity(theta, phi)

fig = plt.figure()

ax = fig.add_subplot(111, projection="mollweide")
ax.grid(True)
ax.tick_params(axis='x', colors='white')

cmap = plt.get_cmap('plasma')
new_cmap = truncate_colormap(cmap, 0, 0.9)
sc = ax.scatter(phi-np.pi, theta-np.pi/2, c=p0_1_ideal,lw=0, s=20,alpha=1,cmap=new_cmap)

cbar = plt.colorbar(sc,orientation="horizontal")
cbar.set_label('Fidelity')
plt.title("Economical Phase Covariant QCM\nIdeal\n")
plt.savefig("economical_phase_covariant.png", dpi=300)

plt.show()