import numpy as np
from preparation_measurement import *
from readout_correction import *
import vars as var
from qiskit import IBMQ

IBMQ.save_account('c9e1fffae385042db3637a8ec55919b328f977bad06cc739bfa8678b831bb9d35ef9e4459f01b42d98c591d47b5add6a5105f57a3068a98cfb88095c05ca737e', overwrite=True)
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


def write_readout_parameters(readout, backend_identifier):
    """
    Write results of readout parameters in a file
    """

    with open('./' + 'results_readout_' + backend_identifier + '.txt', 'a') as file:

        for i in range(len(readout)):
            for j in range(len(readout[i])):
                file.write(str(readout[i][j])+'\t')
        file.write('\n')


def write_copying_results(coords, results, label, backend_identifier):
    """
    Write results of qubit measurements in a file
    """

    with open('./' + 'results_' + label + backend_identifier + '.txt', 'a') as file:
        file.write(str(coords[0]) + "\t" + str(coords[1]) + "\t")
        for i in range(len(results[-1])):
            file.write(
                str(results[-1][i]) + "\t")
        file.write('\n')

def write_average_fidelities(results_list, backend_identifier):
    """
    Write fidelities for corrected and original results.
    """

    labels = ['','corrected']
    for i in range(len(results_list)):
        with open('./' + 'average_fidelities.txt', 'a') as file:
            file.write(
                backend_identifier+"_"+str(labels[i])+"\t" + str(np.average(np.array(results_list[i])[:, 0])) + "\t" + str(
                    np.std(np.array(results_list[i])[:, 0])) + "\t" + str(
                    np.average(np.array(results_list[i])[:, 2])) + "\t" +
                str(np.std(np.array(results_list[i])[:, 2])) + "\n")


def save_experiment(batch, results_probabilities, corrected_results, readout_params, backend_identifier,num_pts):
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
                
        #Readout calibration
        reordered_results = [results_probabilities[-1][i:i+2] for i in range(0,len(results_probabilities[-1])-1,2)]
        corrected_results.append(correct_copies(readout_params, reordered_results))

        #Write corrected results
        write_copying_results(coords, corrected_results,'corrected_',backend_identifier)
        write_copying_results(coords, results_probabilities,'',backend_identifier)
                
        print(len(results_probabilities), "/", num_pts)
    
    return results_probabilities, corrected_results



