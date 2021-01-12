import numpy as np

path = "Economical/Starmon/BB84/"
backend_identifier = "starmon_corrected"
filename = path + "results_" + backend_identifier + ".txt"

theta, phi, p0_1, p1_1, p0_2, p1_2 = np.loadtxt(filename, unpack=True, usecols=(0, 1, 2, 3, 4, 5))

results_probabilities = []
for result in zip(p0_1, p1_1, p0_2, p1_2):
    single_result_list = [result[0], result[1], result[2], result[3]]
    results_probabilities.append(single_result_list)

# Write average fidelities
with open(path + 'average_fidelities.txt', 'a') as file:
    file.write(
        backend_identifier + "\t" + str(np.average(np.array(results_probabilities)[:, 0])) + "\t" + str(
            np.std(np.array(results_probabilities)[:, 0])) + "\t" + str(
            np.average(np.array(results_probabilities)[:, 2])) + "\t" +
        str(np.std(np.array(results_probabilities)[:, 2])) + "\n")
