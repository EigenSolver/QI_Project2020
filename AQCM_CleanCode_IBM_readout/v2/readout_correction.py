import numpy as np
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, assemble, transpile
from qiskit import IBMQ
from preparation_measurement import *


def make_readout_circuits():
    """Single qubit calibration run independently for all the qubits in the circuit"""

    circuits = []
    n = 2

    for index in range(n):
        qc_0 = QuantumCircuit(n, 1)
        qc_1 = QuantumCircuit(n, 1)
        qc_1.x(index)
        qc_0.measure(index, 0)
        qc_1.measure(index, 0)
        circuits.append([qc_0, qc_1])

    return circuits


def readout_analyze_data(job_to_analyze, nshots):
    """
    Returns an array of marginal probabilities for the experiments run in job_to_analyze
    """
    # Get the counts in each job and merge everything into only one array
    correcting_parameters = []
    counts_array = get_counts_from_jobs([job_to_analyze])
    # print('readout analyze data')
    # print(counts_array)
    reorder_count_array = [counts_array[2 * i:(i) * 2 + 2] for i in range(0, len(counts_array) // 2)]
    # print(reorder_count_array)
    # Calculate the marginal probabilities from the counts histograms.
    for job in reorder_count_array:
        correcting_parameters.append(readout_correction(job, nshots))
    # print(correcting_parameters)
    return correcting_parameters


def get_parameters(p0, p1):
    """
    Calculate coefficients beta0 and beta1 for classical readout correction
    """
    beta_1 = 0.5 * (p0 + p1)
    beta_2 = 0.5 * (p0 - p1)

    return beta_1, beta_2


def readout_correction(job, nshots):
    """
    Returns an array of marginal probabilities for the experiments run in job_to_analyze
    """
    
    p0_0 = job[0]['0']/nshots
    mz_0 = p0_0 if p0_0 == 1.0 else p0_0 - job[0]['1']/nshots


    p1_1 = job[1]['1']/nshots
    mz_1 = -p1_1 if p1_1 == 1.0 else -p1_1 + job[1]['0']/nshots


    # print(job.result().get_counts())
    return get_parameters(mz_0, mz_1)


def correct_copies(b, p):
    """
    The results for the probabilities p_0 and p_1 are corrected using the readout parameters b.
    """
    corrected_results = []
    # print(b,p)

    # print(p)

    for i in range(len(b)):
        q0_corr = (b[i][1] - b[i][0] + p[i][0] - p[i][1]) / (2 * b[i][1])
        q1_corr = 1 - q0_corr
        corrected_results += [q0_corr] + [q1_corr]

    # print(corrected_results)

    return corrected_results


def run_readout_correction(readout_obj, nshots, backend):
    print("Readout calibration...")
    readout_params = readout_analyze_data(backend.run(readout_obj), nshots)
    if readout_params == []:
        print("error no readout")

    # print(readout_params)
    return readout_params
