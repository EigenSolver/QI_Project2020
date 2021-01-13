import matplotlib.pyplot as plt
import numpy as np

# THINGS YOU HAVE TO MODIFY

# Put the path where you want to save the output opicture
save_pic_path="Economical/histo_sphere_noerrors.png"
# Put the title of the picture
title = "EPCQCM - Sphere"
# Put the path for IBM averages
path_IBM = "Economical/IBM/FullSphere/average_fidelities.txt"
# Put the path for Starmon averages
path_starmon = "Economical/Starmon/FullSphere/average_fidelities.txt"
# Put the path for Spin2 averages (just leave this if you are not using it)
path_spin2 = "Economical/Spin2/FullSphere/average_fidelities.txt"
# Choose whether you are using spin2 or not
use_spin2=True
# Set the number of points
npoints=1000 #Used to calculate uncertainty on the mean (stddev/sqrt(n))
# Set whether to show the error bars
error_bars_active=False
# Uncomment the expected fidelity for your case and comment the others
expected_fidelity=(7+2*np.sqrt(2))/12
#expected_fidelity = 5/6
#expected_fidelity = 1 / 2 + 1 / (2 * np.sqrt(2))


# labels and dictionary to read data automatically
labels = ['Starmon-5', 'Athens', 'Ourense', 'Santiago', 'Valencia', 'Vigo', 'Yorktown']
dict = {"starmon:": 0, "athens_": 1, "ourense_": 2, "santiago_": 3, "valencia_": 4,"vigo_corrected": 5, "ibmqx2_": 6}
dict_corrected = {"starmon_corrected": 0, "athens_corrected": 1, "ourense_corrected": 2, "santiago_corrected": 3,
                  "valencia_corrected": 4,"vigo_corrected": 5, "ibmqx2_corrected": 6}

# Read data from different files
name, fidelity_copy_1, stddev_copy_1, fidelity_copy_2, stddev_copy_2 = np.genfromtxt(path_IBM, delimiter="\t",
                                                                                     dtype=str, unpack=True)
name_starmon, fidelity_copy_1_starmon, stddev_copy1_starmon, fidelity_copy_2_starmon, stddev_copy2_starmon = np.genfromtxt(
    path_starmon, delimiter="\t", dtype=str, unpack=True)
name=np.append(name, name_starmon)
fidelity_copy_1=np.append(fidelity_copy_1,fidelity_copy_1_starmon)
stddev_copy_1=np.append(stddev_copy_1,stddev_copy1_starmon)
fidelity_copy_2=np.append(fidelity_copy_2,fidelity_copy_2_starmon)
stddev_copy_2=np.append(stddev_copy_2,stddev_copy2_starmon)

if use_spin2:
    labels = ['Spin-2', 'Starmon-5', 'Athens', 'Ourense', 'Santiago', 'Valencia', 'Vigo', 'Yorktown']
    dict = {"spin2": 0, "starmon:": 1, "athens_": 2, "ourense_": 3, "santiago_": 4, "valencia_": 5, "vigo_corrected": 6,
            "ibmqx2_": 7}
    dict_corrected = {"spin2_corrected": 0, "starmon_corrected": 1, "athens_corrected": 2, "ourense_corrected": 3,
                      "santiago_corrected": 4,
                      "valencia_corrected": 5, "vigo_corrected": 6, "ibmqx2_corrected": 7}
    name_spin2, fidelity_copy_1_spin2, stddev_copy1_spin2, fidelity_copy_2_spin2, stddev_copy2_spin2 = np.genfromtxt(
        path_spin2, delimiter="\t", dtype=str, unpack=True)
    name = np.append(name, name_spin2)
    fidelity_copy_1 = np.append(fidelity_copy_1, fidelity_copy_1_spin2)
    stddev_copy_1 = np.append(stddev_copy_1, stddev_copy1_spin2)
    fidelity_copy_2 = np.append(fidelity_copy_2, fidelity_copy_2_spin2)
    stddev_copy_2 = np.append(stddev_copy_2, stddev_copy2_spin2)

# Convert string to float
fidelity_copy_1 = fidelity_copy_1.astype(np.float)
stddev_copy_1 = stddev_copy_1.astype(np.float)
fidelity_copy_2 = fidelity_copy_2.astype(np.float)
stddev_copy_2 = stddev_copy_2.astype(np.float)

# Start filtering to get only the corrected values (change dict_corrected for the others)
fidelity_copy_1_filtered = np.zeros(len(labels))
stddev_copy_1_filtered = np.zeros(len(labels))
fidelity_copy_2_filtered = np.zeros(len(labels))
stddev_copy_2_filtered = np.zeros(len(labels))
for i in range(len(name)):
    if name[i] in dict_corrected:
        fidelity_copy_1_filtered[dict_corrected[name[i]]] = fidelity_copy_1[i]
        stddev_copy_1_filtered[dict_corrected[name[i]]] = stddev_copy_1[i]
        fidelity_copy_2_filtered[dict_corrected[name[i]]] = fidelity_copy_2[i]
        stddev_copy_2_filtered[dict_corrected[name[i]]] = stddev_copy_2[i]

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

# Plotting details
SMALL_SIZE = 8
MEDIUM_SIZE = 15
BIG_SIZE = 22

plt.rc('font', size=MEDIUM_SIZE)  # controls default text sizes
plt.rc('axes', titlesize=MEDIUM_SIZE)  # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
plt.rc('xtick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)  # legend fontsize
plt.rc('figure', titlesize=BIG_SIZE)  # fontsize of the figure title

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot([0 - width, x[-1] + width], [expected_fidelity, expected_fidelity], color='tab:green', linewidth=3,
        label='Ideal',zorder=0)
if error_bars_active:
    rects1 = ax.bar(x - width / 2, fidelity_copy_1_filtered, width, label='Copy 1', yerr=stddev_copy_1_filtered/np.sqrt(npoints), capsize=10)
    rects2 = ax.bar(x + width / 2, fidelity_copy_2_filtered, width, label='Copy 2', yerr=stddev_copy_2_filtered/np.sqrt(npoints),capsize=10)
else:
    rects1 = ax.bar(x - width / 2, fidelity_copy_1_filtered, width, label='Copy 1')
    rects2 = ax.bar(x + width / 2, fidelity_copy_2_filtered, width, label='Copy 2')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Fidelity')
ax.set_title(title)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylim(0.625, 0.925)
ax.legend(loc="upper right")

fig.tight_layout()

plt.savefig(save_pic_path,dpi=300)
#plt.show()
