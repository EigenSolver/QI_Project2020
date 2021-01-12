import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
import sys

# file path for the input data
file_path = sys.argv[1]
# title on the picture
title = sys.argv[2]
# number of shots
nshots = int(sys.argv[3])
#is the data from universal qcm? used to plot expected fidelity
is_universal = int(sys.argv[4])

if is_universal:
    expected_fidelity=5/6
else:
    expected_fidelity = 1 / 2 + 1 / (2 * np.sqrt(2))

#each shot is a bernoulli trial with variance p(1-p), where p is the probability of success
#with nshots, the expected uncertainty is sqrt(p(1-p)/nshots)
expected_uncertainty = np.sqrt(expected_fidelity*(1-expected_fidelity)) / np.sqrt(nshots)

# Read coordinates and fidelities for the two copies
theta, phi, p0_1, p0_2 = np.loadtxt(file_path, delimiter="\t", usecols=(0, 1, 2, 4), unpack=True)

# calculate average and standard deviation of measured data
average_fidelity_1 = np.average(p0_1)
std_dev_1 = np.std(p0_1)
average_fidelity_2 = np.average(p0_2)
std_dev_2 = np.std(p0_2)

# prepare lists to store bb84 states
bb84_thetas = []
bb84_p0_1 = []
bb84_p0_2 = []

#rearrange theta to make it run from 0 to 2pi if necessary
for i in range(len(theta)):
    if np.abs(phi[i] + np.pi) < 1E-3:  # if phi=-pi, add pi to theta (so we can still consider phi=0 to plot)
        theta[i] = theta[i] + np.pi
    if phi[i] > np.pi:
        theta[i] = theta[i] + np.pi
    if np.abs(theta[i] % (np.pi / 2)) < 1E-6:  # save the point in a separate list if it's a bb84 point
        bb84_thetas.append(theta[i])
        bb84_p0_1.append(p0_1[i])
        bb84_p0_2.append(p0_2[i])

# Remove the ".txt" extension of the input file
file_path = file_path[:-4]  # remove the last four characters of the path

# Plotting details
plt.rc('text', usetex=True)
fig1 = plt.figure(1)
ax1 = fig1.add_subplot(111)
ax1.grid(True)
ax1.set_xlabel(r'$\theta$', fontsize=15)
ax1.set_ylabel('Fidelity', fontsize=15)
ax1.plot([0, 2 * np.pi], [expected_fidelity, expected_fidelity], color="tab:green",
         label=r'$F_{ideal}$',linewidth=3)  # Expected fidelity
ax1.plot([0, 2 * np.pi], [average_fidelity_1, average_fidelity_1], label=r'$F_1$',linewidth=3)  # Measured average fidelity
ax1.plot([0, 2 * np.pi], [average_fidelity_1 + std_dev_1, average_fidelity_1 + std_dev_1], linestyle="dashed",
         color="tab:blue", label=r'$F_1 \pm \sigma_{F_1}$')  # Plot horiziontal line
ax1.plot([0, 2 * np.pi], [average_fidelity_1 - std_dev_1, average_fidelity_1 - std_dev_1], linestyle="dashed",
         color="tab:blue")  # Plot horiziontal line
ax1.plot([0, 2 * np.pi], [average_fidelity_1 + expected_uncertainty, average_fidelity_1 + expected_uncertainty],
         linestyle="dashed", color="tab:red", label=r'$F_1 \pm \sigma_{stat}$')  # Plot horiziontal line
ax1.plot([0, 2 * np.pi], [average_fidelity_1 - expected_uncertainty, average_fidelity_1 - expected_uncertainty],
         linestyle="dashed", color="tab:red")  # Plot horiziontal line
ax1.scatter(theta, p0_1,zorder=3)
ax1.scatter(bb84_thetas,bb84_p0_1,color="tab:orange", label=r"$BB84$",zorder=3)
ax1.set_xticks([0,np.pi/4, np.pi/2, 3*np.pi/4,np.pi,5*np.pi/4, 3*np.pi/2, 7*np.pi/4,2*np.pi])
ax1.set_xticklabels(['$0$',r'$\frac{\pi}{4}$', r'$\frac{\pi}{2}$',r'$\frac{3\pi}{4}$', r'$\pi$',r'$\frac{5\pi}{4}$', r'$\frac{3\pi}{2}$',r'$\frac{7\pi}{4}$', r'$2\pi$'])
ax1.set_title(title+"\n Copy 1",pad=20,fontsize=20)
ax1.tick_params(axis='y', which='major', labelsize=15)
ax1.tick_params(axis='x', which='major', labelsize=20)
plt.legend()
plt.tight_layout()
plt.subplots_adjust(left=0.15, right=0.95)
fig1.savefig(file_path + "_copy1.png", dpi=300)
#plt.show()

fig2 = plt.figure(2)
ax2 = fig2.add_subplot(111)
ax2.grid(True)
ax2.set_xlabel(r'$\theta$', fontsize=15)
ax2.set_ylabel('Fidelity', fontsize=15)
ax2.plot([0, 2 * np.pi], [expected_fidelity, expected_fidelity], color="tab:green",
         label=r'$F_{ideal}$',linewidth=3)  # Expected fidelity
ax2.plot([0, 2 * np.pi], [average_fidelity_2, average_fidelity_2], label=r'$F_2$',linewidth=2)  # Measured average fidelity
ax2.plot([0, 2 * np.pi], [average_fidelity_2 + std_dev_2, average_fidelity_2 + std_dev_2], linestyle="dashed",
         color="tab:blue", label=r'$F_2 \pm \sigma_{F_2}$')  # Plot horiziontal line
ax2.plot([0, 2 * np.pi], [average_fidelity_2 - std_dev_2, average_fidelity_2 - std_dev_2], linestyle="dashed",
         color="tab:blue")  # Plot horiziontal line
ax2.plot([0, 2 * np.pi], [average_fidelity_2 + expected_uncertainty, average_fidelity_2 + expected_uncertainty],
         linestyle="dashed", color="tab:red", label=r'$F_2 \pm \sigma_{stat}$')  # Plot horiziontal line
ax2.plot([0, 2 * np.pi], [average_fidelity_2 - expected_uncertainty, average_fidelity_2 - expected_uncertainty],
         linestyle="dashed", color="tab:red")  # Plot horiziontal line
ax2.scatter(theta, p0_2,zorder=3)
ax2.scatter(bb84_thetas,bb84_p0_2,color="tab:orange", label=r"$BB84$",zorder=3)
ax2.set_xticks([0,np.pi/4, np.pi/2, 3*np.pi/4,np.pi,5*np.pi/4, 3*np.pi/2, 7*np.pi/4,2*np.pi])
ax2.set_xticklabels(['$0$',r'$\frac{\pi}{4}$', r'$\frac{\pi}{2}$',r'$\frac{3\pi}{4}$', r'$\pi$',r'$\frac{5\pi}{4}$', r'$\frac{3\pi}{2}$',r'$\frac{7\pi}{4}$', r'$2\pi$'])
ax2.set_title(title+"\n Copy 2",pad=20,fontsize=20)
ax2.tick_params(axis='y', which='major', labelsize=15)
ax2.tick_params(axis='x', which='major', labelsize=20)
plt.legend()
plt.tight_layout()
plt.subplots_adjust(left=0.15, right=0.95)
fig2.savefig(file_path + "_copy2.png", dpi=300)
#plt.show()