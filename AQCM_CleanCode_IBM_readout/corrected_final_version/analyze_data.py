import numpy as np
from preparation_measurement import *
from readout_correction import *
from qiskit import IBMQ

IBMQ.save_account('396ead77546bea5bd0a82c923c3af4291041412498d68092223ae8e2f2a95f9f34ef93c1416d1b3b62af52f3980571a82eddc3e5951a96d643152b907cfa37aa', overwrite=True)
provider = IBMQ.load_account()

def get_backend(inputt):
    inputt = str(inputt)
    #print(inputt)
    list_backend_identifiers = ['simulator',
                                'ibmqx2',
                                'melbourne',
                                'vigo',
                                'ourense',
                                'valencia',
                                'athens',
                                'santiago']

    list_backends = [provider.backends.ibmq_qasm_simulator,
                     provider.backends.ibmqx2,
                     provider.backends.ibmq_16_melbourne,
                     provider.backends.ibmq_vigo,
                     provider.backends.ibmq_ourense,
                     provider.backends.ibmq_valencia,
                     provider.backends.ibmq_athens,
                     provider.backends.ibmq_santiago]

    if inputt in list_backend_identifiers:

        index = list_backend_identifiers.index(inputt)
        return inputt, list_backends[index]

    else:
        return list_backend_identifiers[0], list_backends[0]


def write_readout_parameters(readout, backend_identifier, path):
    """
    Write results of readout parameters in a file
    """

    with open(path + 'results_readout_' + backend_identifier + '.txt', 'a') as file:

        for i in range(len(readout)):
            for j in range(len(readout[i])):
                file.write(str(readout[i][j])+'\t')
        file.write('\n')


def write_copying_results(coords, results, label, backend_identifier, path):
    """
    Write results of qubit measurements in a file
    """

    with open(path + 'results_' + label + backend_identifier + '.txt', 'a') as file:
        file.write(str(coords[0]) + "\t" + str(coords[1]) + "\t")
        for i in range(len(results[-1])):
            file.write(
                str(results[-1][i]) + "\t")
        file.write('\n')

def write_average_fidelities(results_list, backend_identifier, path):
    """
    Write fidelities for corrected and original results.
    """

    labels = ['','corrected']
    for i in range(len(results_list)):
        with open(path + 'average_fidelities.txt', 'a') as file:
            file.write(
                backend_identifier+"_"+str(labels[i])+"\t" + str(np.average(np.array(results_list[i])[:, 0])) + "\t" + str(
                    np.std(np.array(results_list[i])[:, 0])) + "\t" + str(
                    np.average(np.array(results_list[i])[:, 2])) + "\t" +
                str(np.std(np.array(results_list[i])[:, 2])) + "\n")


def save_experiment(batch, results_probabilities, corrected_results, readout_params, backend_identifier,target_points, path):
    """
    Receives measurement results and readout parameters, correct the measurements
    and write resulting data in files
    """

    # Append the results and print them one by one
    for result in batch:
        results_probabilities.append(result)
        coords = (
            target_points[len(results_probabilities) - 1][0],
            target_points[len(results_probabilities) - 1][1])
                
        #Readout calibration
        reordered_results = [results_probabilities[-1][i:i+2] for i in range(0,len(results_probabilities[-1])-1,2)]
        corrected_results.append(correct_copies(readout_params, reordered_results))

        #Write corrected results
        write_copying_results(coords, corrected_results,'corrected_',backend_identifier, path)
        write_copying_results(coords, results_probabilities,'',backend_identifier, path)
                
        #print(len(results_probabilities), "/", num_pts)
    
    return results_probabilities, corrected_results



