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
IBMQ.save_account(TOKEN_IBMQ, overwrite=True)
provider = IBMQ.load_account()
backend = provider.backends.ibmqx2
# ibmq_qasm_simulator for simulator
# ibmq_16_melbourne for melbourne
# ibmqx2 for yorktown
# ibmq_nameofthecity for all the others

backend_identifier = "yorktown"  # This string is used to save all the different files
path = "FullSphere/PhaseCovariant/"  # Path where the files will be saved (set whatever you want, create folder before using it)

# Prepare sampling points
num_pts = 1000
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
print("First circuit not transpiled: ")
print(circuits[0])
print("First circuit transpiled: ")
print(circuits_transpiled[0])

# index_copy1_transpiled = circuits_transpiled[0].layout[qubit_copy1.index].index
# index_copy2_transpiled = circuits_transpiled[0].layout[qubit_copy2.index].index

# =======================================================================================================
# RUN THE CIRCUITS
# =======================================================================================================

# Run the circuits always queueing the maximum number of circuits allowed.
running_jobs = []
results_probabilities = []
index = 0
while index * max_experiments < num_pts:
    # Split the transpiled circuits array in an array that contains the maximum number of circuits allowed to run at
    # the same time
    first_circuit_index = index * max_experiments
    # The last slice could be smaller if num_pts is not a multiple of max_experiments
    last_circuit_index = np.minimum((index + 1) * max_experiments, num_pts)

    # Actually take the slice of the original array
    max_circuits_transpiled = [circuit for circuit in circuits_transpiled[first_circuit_index:last_circuit_index]]

    # Create and run the maximum number of experiments
    qobj = assemble(max_circuits_transpiled, backend=backend, shots=max_shots)

    # Run the circuits and save the job in an arrray
    running_jobs.append(backend.run(qobj))

    # Save the (last) job id in a file
    print("Running circuits: ", str(first_circuit_index + 1), " - ", str(last_circuit_index), "/", str(num_pts))
    with open(path + 'job_ids_' + backend_identifier + '.txt', 'a') as file:
        file.write(running_jobs[-1].job_id() + "\n")

    # =========================================================================================
    # Wait for the results before going on and print the results in real time
    # =========================================================================================

    if backend.provider() == QI:  # For Quantum Inspire max 1 job at a time
        print("Waiting for a job to finish...")
        running_jobs[0].result()  # The execution is stopped until the results arrive
        # Calculate the marginal probabilities for the experiment that has just finished running
        results_probabilities_batch = analyze_data(running_jobs[0], index_copy1, index_copy2, max_shots)
        # Append the results and print them one by one
        for result in results_probabilities_batch:
            results_probabilities.append(result)
            coords = (
                target_points[len(results_probabilities) - 1][0],
                target_points[len(results_probabilities) - 1][1])
            with open(path + 'results_' + backend_identifier + '.txt', 'a') as file:
                file.write(
                    str(coords[0]) + "\t" + str(coords[1]) + "\t" + str(
                        results_probabilities[-1][0]) + "\t" + str(
                        results_probabilities[-1][1]) + "\t" +
                    str(results_probabilities[-1][2]) + "\t" + str(results_probabilities[-1][3]) + "\n")
            print(len(results_probabilities), "/", num_pts)
            print("Coordinates theta,phi: ", coords)
            print("Fidelities copy1,copy2: ", [results_probabilities[-1][0], results_probabilities[-1][2]])
            print("Average fidelity copy1, copy2: ", [np.average(np.array(results_probabilities)[:, 0]),
                                                      np.average(np.array(results_probabilities)[:, 2])])
        running_jobs.pop(0)
    else:
        if backend.job_limit().active_jobs == backend.job_limit().maximum_jobs:
            print("Waiting for a job to finish...")
            running_jobs[0].result()  # Wait for the first job to finish
            # Calculate the marginal probabilities for the experiment that has just finished running
            results_probabilities_batch = analyze_data(running_jobs[0], index_copy1, index_copy2, max_shots)
            # Append the results and print them one by one
            for result in results_probabilities_batch:
                results_probabilities.append(result)
                coords = (
                    target_points[len(results_probabilities) - 1][0],
                    target_points[len(results_probabilities) - 1][1])
                with open(path + 'results_' + backend_identifier + '.txt', 'a') as file:
                    file.write(
                        str(coords[0]) + "\t" + str(coords[1]) + "\t" + str(
                            results_probabilities[-1][0]) + "\t" + str(
                            results_probabilities[-1][1]) + "\t" +
                        str(results_probabilities[-1][2]) + "\t" + str(results_probabilities[-1][3]) + "\n")
                print(len(results_probabilities), "/", num_pts)
                print("Coordinates theta,phi: ", coords)
                print("Fidelities copy1,copy2: ", [results_probabilities[-1][0], results_probabilities[-1][2]])
                print("Average fidelity copy1, copy2: ", [np.average(np.array(results_probabilities)[:, 0]),
                                                          np.average(np.array(results_probabilities)[:, 2])])

            running_jobs.pop(0)  # Delete the first job from the array when it is finished

    index = index + 1

# All the jobs have been sent. Now analyze the jobs that have not been analyzed yet
while len(running_jobs) != 0:
    # Calculate the marginal probabilities for the experiment that has just finished running
    results_probabilities_batch = analyze_data(running_jobs[0], index_copy1, index_copy2, max_shots)
    # Append the results and print them one by one
    for result in results_probabilities_batch:
        results_probabilities.append(result)
        coords = (
            target_points[len(results_probabilities) - 1][0],
            target_points[len(results_probabilities) - 1][1])
        with open(path + 'results_' + backend_identifier + '.txt', 'a') as file:
            file.write(
                str(coords[0]) + "\t" + str(coords[1]) + "\t" + str(
                    results_probabilities[-1][0]) + "\t" + str(
                    results_probabilities[-1][1]) + "\t" +
                str(results_probabilities[-1][2]) + "\t" + str(results_probabilities[-1][3]) + "\n")
        print(len(results_probabilities), "/", num_pts)
        print("Coordinates theta,phi: ", coords)
        print("Fidelities copy1,copy2: ", [results_probabilities[-1][0], results_probabilities[-1][2]])
        print("Average fidelity copy1, copy2: ", [np.average(np.array(results_probabilities)[:, 0]),
                                                  np.average(np.array(results_probabilities)[:, 2])])
    running_jobs.pop(0)  # Delete the first job from the array when it is finished

print("===========================================")
print("FINISHED")
print("===========================================")
print("Final average fidelity copy1, copy2: ", [np.average(np.array(results_probabilities)[:, 0]),
                                                np.average(np.array(results_probabilities)[:, 2])])

with open(path + 'average_fidelities.txt', 'a') as file:
    file.write(
        backend_identifier + "\t" + str(np.average(np.array(results_probabilities)[:, 0])) + "\t" + str(
            np.std(np.array(results_probabilities)[:, 0])) + "\t" + str(
            np.average(np.array(results_probabilities)[:, 2])) + "\t" +
        str(np.std(np.array(results_probabilities)[:, 2])) + "\n")
