from quantuminspire.credentials import save_account
from quantuminspire.qiskit import QI
from preparation_measurement import *
from aqcm_circuits import *
from qiskit.circuit import Parameter
from qiskit import IBMQ

def readout_calibration_0():
    readout_circuit_0 = QuantumCircuit(1)
    return readout_calibration_0

def readout_calibration_1():
    readout_circuit_1 = QuantumCircuit(1)
    readout_circuit_1.x(0)
    return readout_calibration_1
