from quantuminspire.credentials import save_account
from quantuminspire.qiskit import QI
from preparation_measurement import *
from aqcm_circuits import *
from qiskit.circuit import Parameter
from qiskit import IBMQ

# =======================================================================================================
# DATA ANALYSIS
# =======================================================================================================

"""
# Enable account for Quantum Inspire, the token has to be inserted in preparation_measurement
save_account(TOKEN_QI)
QI.set_authentication()
print(QI.backends())
backend = QI.get_backend("Starmon-5")
"""

# Enable account for IBMQ, the token has to be inserted in preparation_measurement
IBMQ.save_account(TOKEN_IBMQ, overwrite=True)
provider = IBMQ.load_account()
backend = provider.backends.ibmq_qasm_simulator

backend_identifier = "simulator"  # This string is used to save all the different files
path = "FullSphere/"  # Path where the files will be saved (set whatever you want, create folder before using it)

num_pts = 1000
target_points = equator_xz_points(num_pts)

# Building the circuit we can get the indices for the copies again (not the best solution)
theta_param, phi_param = Parameter('theta_param'), Parameter('phi_param')
qreg = QuantumRegister(3, 'q')
creg = ClassicalRegister(3, 'c')
circuit = QuantumCircuit(qreg, creg)
qubit_copy1, qubit_copy2 = universal_qcm_SWAP(circuit, qreg[0], qreg[1], qreg[2])
index_copy1 = qubit_copy1.index
index_copy2 = qubit_copy2.index

max_shots = backend.configuration().max_shots
max_experiments = backend.configuration().max_experiments

"""
Here all the results are downloaded again and calculated again.
"""

# Retrieve jobs
read_job_ids = open(path + "job_ids_" + backend_identifier + ".txt").read().splitlines()
counts_array = []
results_probabilities = []
retrieved_jobs = [backend.retrieve_job(jobid) for jobid in read_job_ids]

# Get the counts in each job and merge everything into only one array
counts_array = get_counts_from_jobs(retrieved_jobs)

# Calculate the marginal probabilities from the counts histograms.
for job in counts_array:
    marg_prob0_copy1, marg_prob0_copy2 = calculate_probabilities(job, index_copy1, index_copy2, max_shots)
    marg_prob1_copy1 = 1 - marg_prob0_copy1
    marg_prob1_copy2 = 1 - marg_prob0_copy2
    results_probabilities.append([marg_prob0_copy1, marg_prob1_copy1, marg_prob0_copy2, marg_prob1_copy2])

results_probabilities = np.array(results_probabilities)
# Print the results in a text file
for (point, probabilities) in zip(target_points, results_probabilities):
    with open(path + 'results_post_' + backend_identifier + '.txt', 'a') as file:
        file.write(
            str(point[0]) + "\t" + str(point[1]) + "\t" + str(probabilities[0]) + "\t" + str(probabilities[1]) + "\t" +
            str(probabilities[2]) + "\t" + str(probabilities[3]) + "\n")
