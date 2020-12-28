from quantuminspire.credentials import save_account
from quantuminspire.credentials import enable_account
from quantuminspire.qiskit import QI
from preparation_measurement import *
from aqcm_circuits import *
from qiskit.circuit import Parameter
from qiskit import IBMQ
from qiskit.transpiler import Layout
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
num_pts = 25
target_points = sphere_points(num_pts)
# Set to true if the points only lie on the equator (does not perform phi rotation)
only_equator = False

np.savetxt(path + "target_points_" + backend_identifier + ".csv", target_points)

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

#Find the positions of the physical qubits
layout = []
if backend_identifier != 'simulator':
    for element in circuits_transpiled[0].__dict__['_layout'].get_physical_bits():
        layout.append(element)
else:
    layout=[0,1,2]

#Prepare readout circuits
readout_circuits = []

for i in range(nqubits):
    readout_circuits += make_readout_circuits(nqubits)[i]

readout_circuits_transpiled = transpile(readout_circuits, backend=backend, optimization_level=3,initial_layout=layout[:nqubits])


print("First circuit not transpiled: ")
print(circuits[0])
print("First circuit transpiled: ")
print(circuits_transpiled[0])
print(circuits_transpiled[1])


# =======================================================================================================
# RUN THE CIRCUITS
# =======================================================================================================

# Run the circuits always queueing the maximum number of circuits allowed.
running_jobs = []
results_probabilities = []
corrected_results = []
index = 0
#Assemble readout circuits
readout_obj = assemble(readout_circuits_transpiled, backend=backend, shots=max_shots)

while index * max_experiments < num_pts:

    # Split the transpiled circuits array in an array that contains the maximum number of circuits allowed to run at
    # the same time
    first_circuit_index = index * max_experiments
    # The last slice could be smaller if num_pts is not a multiple of max_experiments
    last_circuit_index = np.minimum((index + 1) * max_experiments, num_pts)

    # Actually take the slice of the original array
    max_circuits_transpiled = [circuit for circuit in circuits_transpiled[first_circuit_index:last_circuit_index]]

    # =========================================================================================
    # Wait for the results before going on and print the results in real time
    # =========================================================================================


    #Run a readout before the first round of experiments

    if True:
        print("Readout calibration...")
        readout_params = readout_analyze_data(backend.run(readout_obj), max_shots)
        if readout_params == []:
            print("error no readout")

        with open(path + 'readout_correction_' + backend_identifier + '.txt', 'a') as readout:
            readout.write(str(index)+'\t')
            for i in range(len(readout_params)):
                readout.write(str(readout_params[i][0])+'\t'+str(readout_params[i][1])+'\t')
            readout.write('\n')


    # Create and run the maximum number of experiments
    qobj = assemble(max_circuits_transpiled, backend=backend, shots=max_shots)
    #readout_obj = assemble(readout_circuits_tra, backend=backend, shots=max_shots)

    # Run the circuits and save the job in an arrray
    running_jobs.append(backend.run(qobj))

    # Save the (last) job id in a file
    print("Running circuits: ", str(first_circuit_index + 1), " - ", str(last_circuit_index), "/", str(num_pts))
    with open(path + 'job_ids_' + backend_identifier + '.txt', 'a') as file:
        file.write(running_jobs[-1].job_id() + "\n")

    if True:
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
                
                
                # Readout calibration
                reordered_results = [results_probabilities[-1][i:i+2] for i in range(0,len(results_probabilities[-1])-1,2)]
                corrected_results = correct_copies(readout_params, reordered_results, [index_copy1,index_copy2])

                #Write corrected results
                with open(path + 'corrected_results_' + backend_identifier + '.txt', 'a') as file:

                    file.write(str(coords[0]) + "\t" + str(coords[1]) + "\t")

                    for i in range(len(reordered_results)):                    
                        file.write(
                            str(corrected_results[i][0]) + "\t" + 
                            str(corrected_results[i][1]) + "\t" )
                    file.write('\n')

                #Write results without correction
                with open(path + 'results_' + backend_identifier + '.txt', 'a') as file:
                    file.write(
                        str(coords[0]) + "\t" + str(coords[1]) + "\t" + 
                        str(results_probabilities[-1][0]) + "\t" + 
                        str(results_probabilities[-1][1]) + "\t" +
                        str(results_probabilities[-1][2]) + "\t" + 
                        str(results_probabilities[-1][3]) + "\t" +"\n")
                #print(len(results_probabilities), "/", num_pts)
                

            running_jobs.pop(0)  # Delete the first job from the array when it is finished

    #Read-out calibration run for IBM and QI
    #For IBM one is done after backend.job_limit().maximum_jobs circuits
    #For QI one is done after the number of experiments


    index = index + 1

# All the jobs have been sent. Now analyze the jobs that have not been analyzed yet
while len(running_jobs) != 0:

    # Calculate the marginal probabilities for the experiment that has just finished running
    results_probabilities_batch = analyze_data(running_jobs[0], index_copy1, index_copy2, max_shots)
    # Append the results and print them one by one
    for result in results_probabilities_batch:
        results_probabilities.append(result)
        #print(results_probabilities)
        coords = (
            target_points[len(results_probabilities) - 1][0],
            target_points[len(results_probabilities) - 1][1])
        
        # Readout calibration
        reordered_results = [results_probabilities[-1][i:i+2] for i in range(0,len(results_probabilities[-1])-1,2)]
        corrected_results.append(correct_copies(readout_params, reordered_results, [index_copy1,index_copy2]))
        #print(corrected_results)
        #Write corrected results
        with open(path + 'corrected_results_' + backend_identifier + '.txt', 'a') as file:

            file.write(str(coords[0]) + "\t" + str(coords[1]) + "\t")

            for i in range(len(corrected_results[-1])):                    
                file.write(
                    str(corrected_results[-1][i][0]) + "\t" + 
                    str(corrected_results[-1][i][1]) + "\t" )

            file.write('\n')
                
        with open(path + 'results_' + backend_identifier + '.txt', 'a') as file:
            file.write(
                str(coords[0]) + "\t" + str(coords[1]) + "\t" + str(
                    results_probabilities[-1][0]) + "\t" + str(
                    results_probabilities[-1][1]) + "\t" +
                str(results_probabilities[-1][2]) + "\t" + str(results_probabilities[-1][3]) + "\n")
        #print(len(results_probabilities), "/", num_pts)
        
    running_jobs.pop(0)  # Delete the first job from the array when it is finished

for i in range(len(corrected_results)):
    corrected_results[i] = corrected_results[i][0]+corrected_results[i][1]
#print(results_probabilities, corrected_results)

write_average_difelity(backend_identifier, path, results_probabilities, '')
write_average_difelity(backend_identifier, path, corrected_results, 'corrected')