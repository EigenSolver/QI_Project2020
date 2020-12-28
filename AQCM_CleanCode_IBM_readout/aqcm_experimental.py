from quantuminspire.credentials import save_account
from quantuminspire.credentials import enable_account
from quantuminspire.qiskit import QI
from preparation_measurement import *
from aqcm_circuits import *
from qiskit.circuit import Parameter
from qiskit import IBMQ
from getpass import getpass
from coreapi.auth import BasicAuthentication
from quantuminspire.api import QuantumInspireAPI

# Enable account for Quantum Inspire, the token has to be inserted in preparation_measurement
"""
enable_account(TOKEN_QI)
QI.set_authentication()
print(QI.backends())
backend = QI.get_backend("Starmon-5")
"""
# Enable account for IBMQ, the token has to be inserted in preparation_measurement
IBMQ.save_account('c9e1fffae385042db3637a8ec55919b328f977bad06cc739bfa8678b831bb9d35ef9e4459f01b42d98c591d47b5add6a5105f57a3068a98cfb88095c05ca737e', overwrite=True)
provider = IBMQ.load_account()
backend = provider.backends.ibmq_qasm_simulator
#ibmq_qasm_simulator for simulator
#ibmq_16_melbourne for melbourne
#ibmqx2 for yorktown
#ibmq_nameofthecity for all the others

backend_identifier = "simulator"  # This string is used to save all the different files
path = "./"  # Path where the files will be saved (set whatever you want, create folder before using it)

# Prepare sampling points
num_pts = 10
target_points = sphere_points(num_pts)
# Set to true if the points only lie on the equator (does not perform phi rotation)
only_equator = False

np.savetxt(path + "target_points_" + backend_identifier + ".csv", target_points)

# =======================================================================================================
# PREPARE THE CIRCUITS
# =======================================================================================================

# Assemble circuit
theta_param, phi_param = Parameter('theta_param'), Parameter('phi_param')
qreg = QuantumRegister(3, 'q')
creg = ClassicalRegister(3, 'c')
circuit = QuantumCircuit(qreg, creg)
circuit_readout_0 = QuantumCircuit(1, 1)
circuit_readout_1 = QuantumCircuit(1, 1)

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

#Prepare readout circuits
circuit_readout_0.measure(0,0)
circuit_readout_1.x(0)
circuit_readout_1.measure(0,0)

readout_circuits = [circuit_readout_0,circuit_readout_1]
readout_circuits_transpiled = transpile(readout_circuits, backend=backend, optimization_level=3)

circuits_transpiled = transpile(circuits, backend=backend, optimization_level=3)
print("First circuit not transpiled: ")
print(circuits[0])
print("First circuit transpiled: ")
print(circuits_transpiled[0])
print(readout_circuits_transpiled[0])
print(readout_circuits_transpiled[1])

# index_copy1_transpiled = circuits_transpiled[0].layout[qubit_copy1.index].index
# index_copy2_transpiled = circuits_transpiled[0].layout[qubit_copy2.index].index

# =======================================================================================================
# RUN THE CIRCUITS
# =======================================================================================================

# Run the circuits always queueing the maximum number of circuits allowed.
running_jobs = []
results_probabilities = []
results_readout = []
index = 0

    # =========================================================================================
    # Wait for the results before going on and print the results in real time
    # =========================================================================================
readout_obj = assemble(readout_circuits_transpiled, backend=backend, shots=max_shots)
running_jobs.append(backend.run(readout_obj))
print("Readout calibration...")
print(running_jobs[0].result().get_counts())  # The execution is stopped until the results arrive
    # Calculate the marginal probabilities for the experiment that has just finished running

readout_params = readout_correction(running_jobs[0],max_shots)
print(readout_params)

print("===========================================")
print("FINISHED")
print("===========================================")
#print("Final average fidelity copy1, copy2: ", [np.average(np.array(results_probabilities)[:, 0]),
 #                                               np.average(np.array(results_probabilities)[:, 2])])
