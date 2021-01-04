import numpy as np
from preparation_measurement import *
from readout_correction import *


def write_readout_parameters(readout, backend_identifier, path, num_pts):
    """
    Write results of readout parameters in a file
    """

    with open(path + 'results_readout_' + backend_identifier + '.txt', 'a') as file:

        for i in range(len(readout)):
            for j in range(len(readout[i])):
                file.write(str(readout[i][j]) + '\t')
        file.write('\n')


def write_copying_results(coords, results, label, backend_identifier, path, num_pts):
    """
    Write results of qubit measurements in a file
    """

    with open(path + 'results_' + label + backend_identifier + '.txt', 'a') as file:
        file.write(str(coords[0]) + "\t" + str(coords[1]) + "\t")
        for i in range(len(results[-1])):
            file.write(
                str(results[-1][i]) + "\t")
        file.write('\n')


def write_average_fidelities(results_list, backend_identifier, path, num_pts):
    """
    Write fidelities for corrected and original results.
    """

    labels = ['', 'corrected']
    for i in range(len(results_list)):
        with open(path + 'average_fidelities.txt', 'a') as file:
            file.write(
                backend_identifier + "_" + str(labels[i]) + "\t" + str(
                    np.average(np.array(results_list[i])[:, 0])) + "\t" + str(
                    np.std(np.array(results_list[i])[:, 0])) + "\t" + str(
                    np.average(np.array(results_list[i])[:, 2])) + "\t" +
                str(np.std(np.array(results_list[i])[:, 2])) + "\n")


def save_experiment(batch, results_probabilities, corrected_results, readout_params, backend_identifier, path, num_pts):
    """
    Receives measurement results and readout parameters, correct the measurements
    and write resulting data in files
    """

    target_points = sphere_points(num_pts)
    # Append the results and print them one by one
    for result in batch:
        results_probabilities.append(result)
        coords = (
            target_points[len(results_probabilities) - 1][0],
            target_points[len(results_probabilities) - 1][1])

        # Readout calibration
        reordered_results = [results_probabilities[-1][i:i + 2] for i in
                             range(0, len(results_probabilities[-1]) - 1, 2)]
        corrected_results.append(correct_copies(readout_params, reordered_results))

        # Write corrected results
        write_copying_results(coords, corrected_results, 'corrected_', backend_identifier, path, num_pts)
        write_copying_results(coords, results_probabilities, '', backend_identifier, path, num_pts)

        print(len(results_probabilities), "/", num_pts)

    return results_probabilities, corrected_results
