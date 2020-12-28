import numpy as np
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, assemble, transpile

TOKEN_QI = 'YOUR_TOKEN'
TOKEN_IBMQ = 'YOUR_TOKEN '


def prepare_qubit(qc, qubit, theta, phi):
    """
    Prepares the state |psi>=cos(theta/2)|0>+e^(i phi)sin(theta/2)|1>
    """
    qc.ry(theta, qubit)
    qc.rz(phi, qubit)


def rotated_measurement(qc, qubit, cbit, theta, phi):
    """
    Performs a measurement on qreg qubit (result in creg) in the {|psi>, |psi_perp>} basis,
    where |psi>=cos(theta/2)|0>+e^(i phi)sin(theta/2)|1>
    """

    qc.rz(-phi, qubit)
    qc.ry(-theta, qubit)

    qc.measure(qubit, cbit)


def prepare_qubit_equator(qc, qubit, theta):
    """
    Prepares the state |psi>=cos(theta/2)|0>+sin(theta/2)|1>
    """
    qc.ry(theta, qubit)


def rotated_measurement_equator(qc, qubit, cbit, theta):
    """
    Performs a measurement on qreg qubit (result in creg) in the {|psi>, |psi_perp>} basis,
    where |psi>=cos(theta/2)|0>+sin(theta/2)|1>
    """
    qc.ry(-theta, qubit)

    qc.measure(qubit, cbit)


def prepare_qubit_bb84(qc, qubit, index):
    """
    Prepare a bb84 state with the following convention
    index=0 -> |0>
    index=1 -> |1>
    index=2 -> |+>
    index=3 -> |->
    """
    if index == 1:
        qc.x(qubit)
    elif index == 2:
        qc.sxdg(qubit)
    elif index == 3:
        qc.sx(qubit)


def rotated_measurement_bb84(qc, qubit, cbit, index):
    """
    Performs a bb84 state measurement with the following convention
    index=0 -> |0>
    index=1 -> |1>
    index=2 -> |+>
    index=3 -> |->
    """
    if index == 1:
        qc.x(qubit)
    elif index == 2:
        qc.sx(qubit)
    elif index == 3:
        qc.sxdg(qubit)
    qc.measure(qubit, cbit)


def sphere_points(num_pts):
    """
    Create num_pts evenly distributed points on a sphere as explained at
    https://stackoverflow.com/questions/9600801/evenly-distributing-n-points-on-a-sphere
    """
    indices = np.arange(0, num_pts, dtype=float) + 0.5

    theta = np.arccos(1 - 2 * indices / num_pts)
    phi = (np.pi * (1 + 5 ** 0.5) * indices) % (2 * np.pi)
    coords = []

    for theta_elem, phi_elem in zip(theta, phi):
        coords.append((theta_elem, phi_elem))

    return np.array(coords)


def equator_xz_points(num_pts):
    """
    Generate num_pts evenly spaced points on the xz equator. It returns their angular coordinates.
    """

    coords = []
    for i in range(num_pts):
        coords.append((2 * np.pi / num_pts * i, 0))

    return np.array(coords)


def equator_xy_points(num_pts):
    """
    Generate num_pts evenly spaced points on the xy equator. It returns their angular coordinates.
    """

    coords = []
    for i in range(num_pts):
        coords.append((np.pi / 2, 2 * np.pi / num_pts * i))

    return np.array(coords)


def bb84_points():
    """
    Generate the coordinates of the bb84 states
    """
    coords = [(0, 0), (np.pi / 2, 0), (np.pi, 0), (3 * np.pi / 2, 0)]

    return np.array(coords)


def calculate_probabilities(job, index_copy1, index_copy2, nshots):
    """
    Calculate the marginal probabilities of getting 0 on each of the two copies qubits
    """
    # Format of the results:
    # {'000': number_of_000, '010': number_of_010, '100': number_of_100, '110': number_of_110}
    marg_prob0_copy1 = 0
    marg_prob0_copy2 = 0
    for outcome in job:
        # If the outcome of the index_copy1 qubit was zero, then add the probability
        if outcome[-1 - index_copy1] == '0':
            marg_prob0_copy1 += job[outcome] / nshots
        # If the outcome of the index_copy2 qubit was zero, then add the probability
        if outcome[-1 - index_copy2] == '0':
            marg_prob0_copy2 += job[outcome] / nshots
    return marg_prob0_copy1, marg_prob0_copy2


def get_counts_from_jobs(jobs):
    """
    Extract the counts from the input jobs
    """
    counts_array = []
    for job in jobs:
        # get_counts() returns a list of Counts (if more experiment were run in the job)
        # or a single object Counts (if only one experiment was run in the job).
        # In order to concatenate (i.e. use the + operator) we have to make sure that job.result().get_counts() is a list
        if isinstance(job.result().get_counts(), list):
            counts_array = counts_array + job.result().get_counts()
        else:
            counts_array = counts_array + [job.result().get_counts()]
    #print(counts_array)
    return counts_array


def analyze_data(job_to_analyze, index_copy1, index_copy2, nshots):
    """
    Returns an array of marginal probabilities for the experiments run in job_to_analyze
    """
    # Get the counts in each job and merge everything into only one array
    results_probabilities = []
    counts_array = get_counts_from_jobs([job_to_analyze])
    # Calculate the marginal probabilities from the counts histograms.
    for job in counts_array:
        marg_prob0_copy1, marg_prob0_copy2 = calculate_probabilities(job, index_copy1, index_copy2,
                                                                     nshots)
        marg_prob1_copy1 = 1 - marg_prob0_copy1
        marg_prob1_copy2 = 1 - marg_prob0_copy2
        results_probabilities.append(
            [marg_prob0_copy1, marg_prob1_copy1, marg_prob0_copy2, marg_prob1_copy2])

    return results_probabilities

def readout_analyze_data(job_to_analyze, nshots):
    """
    Returns an array of marginal probabilities for the experiments run in job_to_analyze
    """
    # Get the counts in each job and merge everything into only one array
    correcting_parameters = []
    counts_array = get_counts_from_jobs([job_to_analyze])
    #print('readout analyze data')
    #print(counts_array)
    reorder_count_array =[counts_array[2*i:(i)*2+2] for i in range(0,len(counts_array)//2)]
    #print(reorder_count_array)
    # Calculate the marginal probabilities from the counts histograms.
    for job in reorder_count_array:
        correcting_parameters.append(readout_correction(job, nshots))
    #print(correcting_parameters)
    return correcting_parameters

def get_parameters(p0, p1):
    """
    Calculate coefficients beta0 and beta1 for classical readout correction
    """
    beta_1 = 0.5*(p0+p1)
    beta_2 = 0.5*(p0-p1)

    return beta_1, beta_2

def readout_correction(job, nshots):
    """
    Returns an array of marginal probabilities for the experiments run in job_to_analyze
    """
    
    p0_0 = job[0]['0']/nshots
    mz_0 = p0_0 if p0_0 == 1.0 else p0_0 - job[0]['1']/nshots


    p1_1 = job[1]['1']/nshots
    mz_1 = -p1_1 if p1_1 == 1.0 else -p1_1 + job[1]['0']/nshots


    #print(job.result().get_counts())
    return get_parameters(mz_0,mz_1)

def check_results_length(betas,probs,indexes):
        if len(p) == len(indexes) and len(p) != len(b):
            pass
        else:
            pass


def correct_copies(b,p,indexes):
    """
    The results for the probabilities p_0 and p_1 are corrected using the readout parameters b.
    """
    corrected_results = []
    #print(b,p)

    if len(p) == len(indexes) and len(p) != len(b):
        p.insert(0,[])

    #print(p)

    for i in indexes:
        q0_corr= (b[i][1]-b[i][0] + p[i][0] -  p[i][1])/(2*b[i][1])
        q1_corr= 1-q0_corr
        corrected_results.append([q0_corr,q1_corr])
        #print(i,p[i],b[i])
    #print(corrected_results)

    return corrected_results

def write_average_difelity(backend_identifier, path, results_probabilities, label):

    with open(path + 'average_'+label+'_fidelities.txt', 'a') as file:
        file.write(
            backend_identifier + "\t" + str(np.average(np.array(results_probabilities)[:, 0])) + "\t" + str(
                np.std(np.array(results_probabilities)[:, 0])) + "\t" + str(
                np.average(np.array(results_probabilities)[:, 2])) + "\t" +
            str(np.std(np.array(results_probabilities)[:, 2])) + "\n")

