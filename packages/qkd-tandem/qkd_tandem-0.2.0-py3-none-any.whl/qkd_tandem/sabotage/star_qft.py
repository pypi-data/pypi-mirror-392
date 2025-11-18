import random
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

backend = AerSimulator()

def star_qft_sabotage(n_qubits, shots=1024):
    qc = QuantumCircuit(n_qubits * 3, n_qubits * 3)
    for i in range(n_qubits):
        a, b, c = i*3, i*3+1, i*3+2
        bit = random.randint(0, 1)
        basis = random.randint(0, 1)
        if bit: qc.x(a)
        if basis: qc.h(a)
        qc.cx(a, b)
        qc.cx(a, c)
        if basis == 0:
            qc.h(c)
        qc.measure(c, n_qubits*2 + i)
        qc.h(b); qc.h(c); qc.h(b)
        if basis:
            qc.h(b); qc.h(a)
        qc.measure(b, n_qubits + i)
        qc.measure(a, i)
    return qc

def run_star_qft(n_bits=4, shots=1024):
    qc = star_qft_sabotage(n_bits, shots=shots)
    result = backend.run(qc, shots=shots).result()
    return result.get_counts()
