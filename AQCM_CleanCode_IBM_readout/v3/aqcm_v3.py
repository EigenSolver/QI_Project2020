from quantuminspire.credentials import save_account
from quantuminspire.credentials import enable_account
from quantuminspire.qiskit import QI
from preparation_measurement import *
from aqcm_circuits import *
from readout_correction import *
from qiskit.circuit import Parameter
from qiskit import IBMQ
from qiskit.transpiler import Layout
from getpass import getpass
from coreapi.auth import BasicAuthentication
from quantuminspire.api import QuantumInspireAPI
from analyze_data import *
import sys
##############################################################################################
num_pts = 10
##############################################################################################
################################ QUANTUM INSPIRE ############################################
# Enable account for Quantum Inspire, the token has to be inserted in preparation_measurement
"""
enable_account(TOKEN_QI)
QI.set_authentication()
print(QI.backends())
backend = QI.get_backend("Starmon-5")
"""
##############################################################################################
######################################## IBM  ################################################
# Enable account for IBMQ, the token has to be inserted in preparation_measurement
backend_identifier, backend = get_backend(sys.argv[1])
print(backend_identifier)
#ibmq_qasm_simulator for simulator
#ibmq_16_melbourne for melbourne
#ibmqx2 for yorktown
#ibmq_nameofthecity for all the others
##############################################################################################

#We are saving the target points along with the results
target_points = sphere_points(num_pts)
#np.savetxt(path + "target_points_" + backend_identifier + ".csv", target_points)

# Set to true if the points only lie on the equator (does not perform phi rotation)
only_equator = False

# =======================================================================================================
# PREPARE THE CIRCUITS
# =======================================================================================================

# Assemble circuit
theta_param, phi_param = Parameter('theta_param'), Parameter('phi_param')
nqubits = 3
qreg = QuantumRegister(nqubits, 'q')
creg = ClassicalRegister(nqubits, 'c')
circuit = QuantumCircuit(qreg, creg)

if not only_equator:
    prepare_qubit(circuit, qreg[0], theta_param, phi_param)
else:
    prepare_qubit_equator(circuit, qreg[0], theta_param)

qubit_copy1, qubit_copy2 = phase_covariant_qcm(circuit, qreg[0], qreg[1], qreg[2])
index_copy1 = qubit_copy1.index
index_copy2 = qubit_copy2.index

if not only_equator:
    rotated_measurement(circuit, qreg[index_copy1], creg[index_copy1], theta_param, phi_param)
    rotated_measurement(circuit, qreg[index_copy2], creg[index_copy2], theta_param, phi_param)
else:
    rotated_measurement_equator(circuit, qreg[index_copy1], creg[index_copy1], theta_param)
    rotated_measurement_equator(circuit, qreg[index_copy2], creg[index_copy2], theta_param)

max_shots = backend.configuration().max_shots
max_experiments = backend.configuration().max_experiments

# Prepare circuits
if not only_equator:
    circuits = [circuit.bind_parameters({theta_param: points[0], phi_param: points[1]}) for points in target_points]
else:
    circuits = [circuit.bind_parameters({theta_param: points[0]}) for points in target_points]

circuits_transpiled = transpile(circuits, backend=backend, optimization_level=3)

#Find the positions of the physical qubits transpiled for the circuit
layout = []

if backend_identifier != 'simulator':
    for element in circuits_transpiled[0].__dict__['_layout'].get_physical_bits():
        layout.append(element)

else:
    layout = range(nqubits)

#print(layout)

#Prepare readout circuits
readout_circuits = make_readout_circuits()
readout_circuits_transpiled = transpile(readout_circuits[0]+readout_circuits[1], backend=backend, optimization_level=3,initial_layout=[layout[index_copy1], layout[index_copy2]])
readout_obj = assemble(readout_circuits_transpiled, backend=backend, shots=max_shots)

print(backend_identifier+": First circuit not transpiled: ")
print(backend_identifier+": First circuit transpiled: ")
print(circuits_transpiled[0])
print(circuits_transpiled[1])
for circuit in readout_circuits_transpiled:
    print(circuit)


# =======================================================================================================
# RUN THE CIRCUITS
# =======================================================================================================

# Run the circuits always queueing the maximum number of circuits allowed.
running_jobs = []
results_probabilities = []
corrected_results = []
index = 0

#Requirements for QI implementation, split readout circuits in individual lists
#because max_experiments = 1

while index * max_experiments < num_pts:

    # Split the transpiled circuits array in an array that contains the maximum number of circuits allowed to run at
    # the same time
    first_circuit_index = index * max_experiments
    # The last slice could be smaller if num_pts is not a multiple of max_experiments
    last_circuit_index = np.minimum((index + 1) * max_experiments, num_pts)

    # Actually take the slice of the original array
    max_circuits_transpiled = [circuit for circuit in circuits_transpiled[first_circuit_index:last_circuit_index]]

    #Run a readout before the first round of experiments and calculate data
    readout_params = run_readout_correction(readout_obj, max_shots, backend)
    write_readout_parameters(readout_params, backend_identifier)

    # Create and run the maximum number of experiments
    qobj = assemble(max_circuits_transpiled, backend=backend, shots=max_shots)

    #Run the circuits and save the job in an arrray
    running_jobs.append(backend.run(qobj))

    #Save and analyze data from last job
    print(backend_identifier+": Waiting for a job to finish...")
    running_jobs[0].result()  # Wait for the first job to finish
    results_probabilities_batch = analyze_data(running_jobs[0], index_copy1, index_copy2, max_shots)
    results_probabilities, corrected_results = save_experiment(results_probabilities_batch, results_probabilities, corrected_results, readout_params, backend_identifier,num_pts) 

    #Eliminate the job from the list and get next one
    running_jobs.pop(0)  # Delete the first job from the array when it is finished
    index = index + 1

    #If it is the last cycle, we evaluate remaining jobs similarly as before
    if index * max_experiments > num_pts:
        while len(running_jobs) != 0:
            results_probabilities_batch = analyze_data(running_jobs[0], index_copy1, index_copy2, max_shots)
            results_probabilities, corrected_results = save_experiment(results_probabilities_batch, results_probabilities, corrected_results, readout_params, backend_identifier, num_pts) 
            running_jobs.pop(0)

#print([results_probabilities, corrected_results])
write_average_fidelities([results_probabilities, corrected_results],backend_identifier)
