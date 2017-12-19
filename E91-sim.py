import numpy as np
import random
import math
import pandas as pd
import pprint

# Importing QISKit
from qiskit import QuantumCircuit, QuantumProgram
import Qconfig

# Import basic plotting tools
from qiskit.tools.visualization import plot_histogram

# Quantum program setup
Q_program = QuantumProgram()
Q_program.set_api(Qconfig.APItoken, Qconfig.config['url']) # set the APIToken and API url

## Input parameters

measuremensChoicesLength = 300 # length of the strings that cointain measurement choices
evePresence = False
evePresencePercentage = 1

## Creating registers

qr = Q_program.create_quantum_register("qr", 2)
cr = Q_program.create_classical_register("cr", 2)

## Backend status

print(Q_program.get_backend_status('ibmqx2'))
print(Q_program.get_backend_status('ibmqx4'))

## Set the backend and coupling map

#ibmqx4_coupling = Q_program.get_backend_configuration('ibmqx4')['coupling_map']

#backend = 'local_qasm_simulator' # simulator
#backend = 'ibmqx4' # real device
backend = 'ibmqx4' # real device  coupling_map=ibmqx4_coupling,

## Creating a shared entangled state

entangledState = Q_program.create_circuit('entangledState', [qr], [cr])

# bell_11 (singlet) stete for the ibmqx4 backend
#entangledState.h(qr[1])
#entangledState.cx(qr[1],qr[0])
#entangledState.x(qr[0])
#entangledState.z(qr[0])

# bell_11 (singlet) stete for the ibmqx2 backend
#entangledState.x(qr[0])
#entangledState.x(qr[1])
#entangledState.h(qr[0])
#entangledState.cx(qr[0],qr[1])

# bell_00 stete for the ibmqx4 backend
entangledState.h(qr[1])
entangledState.cx(qr[1],qr[0])

## Alice's and Bob's measurement choice strings

aliceMeasurementsChoices = []
bobMeasurementsChoices = []

# random strings generation
for i in range(measuremensChoicesLength):
    aliceMeasurementsChoices.append(random.randint(0, 2))
    bobMeasurementsChoices.append(random.randint(0, 2))
	
eveMeasurementsChoices = [[0 for k in range(2)] for j in range(measuremensChoicesLength)]

## Eve's measurement choice array

# The first and the second element of each row represent the measurement of Alice's and Bob's qubit respectively 
# Default values of the array are 0 (applying identity gate)
eveMeasurementsChoices = [[0 for k in range(2)] for j in range(measuremensChoicesLength)]

if evePresence == True:
    for j in range(measuremensChoicesLength):
        if random.uniform(0, 1) <= evePresencePercentage: # in some percent of cases Eve makes her measurement of A's and/or B's qubits
            for k in range(2):
                eveMeasurementsChoices[j][k] = random.randint(0, 7) # random measuremets of A's and B's qubits
				
### Creating measurement circuits

## Alice's measurement circuits

# measurement of spin projection onto (1; 0; 0) vector; standard X-measurement
measureA1 = Q_program.create_circuit('measureA1', [qr], [cr])
measureA1.h(qr[0])
measureA1.measure(qr[0],cr[0])

# measurement of spin projection onto (1/sqt(2); 0; 1/(sqrt(2)) vector
# projection onto (Z+X)/sqrt(2) eigenstates
measureA2 = Q_program.create_circuit('measureA2', [qr], [cr])
measureA2.s(qr[0])
measureA2.h(qr[0])
measureA2.t(qr[0])
measureA2.h(qr[0])
measureA2.measure(qr[0],cr[0])

# measurement of spin projection onto (0; 0; 1) vector; standard Z-measurement
measureA3 = Q_program.create_circuit('measureA3', [qr], [cr])
measureA3.measure(qr[0],cr[0])

## Bob's measurement circuits

# measurement of spin projection onto (1/sqt(2); 0; 1/(sqrt(2)) vector
# projection onto (Z+X)/sqrt(2) eigenstates
measureB1 = Q_program.create_circuit('measureB1', [qr], [cr])
measureB1.s(qr[1])
measureB1.h(qr[1])
measureB1.t(qr[1])
measureB1.h(qr[1])
measureB1.measure(qr[1],cr[1])

# measurement of spin projection onto (0; 0; 1) vector; standard Z-measurement
measureB2 = Q_program.create_circuit('measureB2', [qr], [cr])
measureB2.measure(qr[1],cr[1])

# measurement of spin projection onto (-1/sqt(2); 0; 1/(sqrt(2)) vector
# projection onto (Z-X)/sqrt(2) eigenstates
measureB3 = Q_program.create_circuit('measureB3', [qr], [cr])
measureB3.s(qr[1])
measureB3.h(qr[1])
measureB3.tdg(qr[1])
measureB3.h(qr[1])
measureB3.measure(qr[1],cr[1])

# 1-st qbit identity measurement
ident0 = Q_program.create_circuit('ident0', [qr], [cr])
ident0.iden(qr[0])

# 2-nd qbit identity measurement
ident1 = Q_program.create_circuit('ident1', [qr], [cr])
ident1.iden(qr[1])

## Arrays of Alice's, Bob's and Eve's measurement circuits

aliceMeasurements = [measureA1, measureA2, measureA3]
bobMeasurements = [measureB1, measureB2, measureB3]
eveMeasurements = [ident0, ident1, measureA1, measureA2, measureA3, measureB1, measureB2, measureB3]

circuits = [] # prepared circuits

for k in range(measuremensChoicesLength):
    # create the name of the k-th circuit depending on Alice's and Bob's choices of measurement
    circuitName = str(k) + '-A' + str(aliceMeasurementsChoices[k]+1) + 'B' + str(bobMeasurementsChoices[k]+1) + 'E' + str(eveMeasurementsChoices[k][0]) + str(eveMeasurementsChoices[k][1])
    # create the joint measurement circuit
    Q_program.add_circuit(circuitName, entangledState + eveMeasurements[eveMeasurementsChoices[k][0]] + eveMeasurements[eveMeasurementsChoices[k][1]] + aliceMeasurements[aliceMeasurementsChoices[k]] + bobMeasurements[bobMeasurementsChoices[k]]) 
    circuits.append(circuitName) # add measurement of singlet to circuits array
	
## Execute circuits

simulate = Q_program.execute(circuits, backend='local_qasm_simulator', shots=1, max_credits=12, wait=60, timeout=0, silent=False)
#result = Q_program.execute(circuits, backend=backend, shots=1, max_credits=12, wait=60, timeout=0, silent=False)

## Check measurement errors

# After measurement in A2B1 and A3B2 basis the posterior state must be |00> or |11>. This is an ideal case.
# This block counts how many |01> and |10> states obtained after A2B1 and A3B2 measurements.
# Actual for running on a real device and with Eve's presence.

countsDataFrame = []
for circ in circuits:
    countsDataFrame.append(simulate.get_counts(circ))
countsDataFrame = pd.DataFrame(countsDataFrame)

jointMeasurementChoices = []
for k in range(measuremensChoicesLength):
    jointMeasurementChoices.append('A' + str(aliceMeasurementsChoices[k]+1) + 'B' + str(bobMeasurementsChoices[k]+1))
jointMeasurementChoices = pd.Series(jointMeasurementChoices, name='Measurement')
    
measurementResults = []
possibleStates = ['00', '01', '10', '11']
for k in range(measuremensChoicesLength):
    for j in range(4):
        if pd.notna(countsDataFrame.iat[k,j]) == True:
            measurementResults.append(possibleStates[j])
measurementResults = pd.Series(measurementResults, name='Result')

measuremetsDataFrame = pd.concat([jointMeasurementChoices, measurementResults], axis=1)

errorCounter = 0 # number of measurement errors
for k in range(measuremensChoicesLength):
    if measuremetsDataFrame.iat[k,0] == 'A2B1' and (measuremetsDataFrame.iat[k,1] == '01' or measuremetsDataFrame.iat[k,1] == '10'):
        errorCounter += 1
    if measuremetsDataFrame.iat[k,0] == 'A3B2' and (measuremetsDataFrame.iat[k,1] == '01' or measuremetsDataFrame.iat[k,1] == '10'):
        errorCounter += 1

## Writing measurement results

aliceResults = [] # Alice's results
bobResults = [] # Bob's results

for circ in circuits:
    res = simulate.get_counts(circ) # type = dictionary; in this case it has one key (state) and one value
    if '00' in res: # check if the key is 00 (if posterior state is |00>)
        aliceResults.append(-1) # Alice got the result -1 
        bobResults.append(-1) # Bob got the result -1 
    if '01' in res: # check if the key is 01 (if posterior state is |01>)
        aliceResults.append(-1) # Alice got the result -1 
        bobResults.append(1) # Bob got the result +1 
    if '10' in res:
        aliceResults.append(1)
        bobResults.append(-1)
    if '11' in res:
        aliceResults.append(1)
        bobResults.append(1)
		
## Basis choises check stage
#
# Alice and Bob reveal their strings with basis choices
#
# If in the k-th measurement A and B used the same basis,
# then they write the result of the k-th measurement as the bit of the sifted key 

aliceSiftedKey = [] # Alice's siffted key string
bobSiftedKey = [] # Bob's siffted key string

siftedKeyLength = 0 # length of the sifted key

# the sifted key consist of the results obtained by projecting onto the same eigenstates
# that is A2+B1 and A3+B2 measurements
for k in range(measuremensChoicesLength):
    if (aliceMeasurementsChoices[k] == 1 and bobMeasurementsChoices[k] == 0) or (aliceMeasurementsChoices[k] == 2 and bobMeasurementsChoices[k] == 1):
        aliceSiftedKey.append(aliceResults[k]) # write Alice's k-th result as a key bit
        bobSiftedKey.append(bobResults[k]) # write Bob's k-th result as a key bit; must be inversed for the singlet state
        siftedKeyLength += 1

## Comparing bits of the sifted key

keyMismatchesNumber = 0 # the number of mismatching bits in the sifted key

for k in range(siftedKeyLength):
    if aliceSiftedKey[k] != bobSiftedKey[k]:
        keyMismatchesNumber += 1
		
## CHSH inequality test

# arrays with counts of posterior states
# each element represents the number of |00>, |01>, |10> and |11> posterior states respectively
countA1B1 = [0, 0, 0, 0]
countA1B3 = [0, 0, 0, 0]
countA3B1 = [0, 0, 0, 0]
countA3B3 = [0, 0, 0, 0]

# numbers of posterior states obtained from measurements in a particular basis
count11 = 0
count13 = 0
count31 = 0
count33 = 0

normalizer = 0 # normalizing factor; the total number of A1B1, A1B3, A3B1 and A3B3 measurements

for k in range(measuremensChoicesLength):
    
    res = simulate.get_counts(circuits[k])
    
    if (aliceMeasurementsChoices[k] == 0 and bobMeasurementsChoices[k] == 0):
        if '00' in res:
            countA1B1[0] += 1
        if '01' in res:
            countA1B1[1] += 1
        if '10' in res:
            countA1B1[2] += 1
        if '11' in res:
            countA1B1[3] += 1
        normalizer += 1
        count11 += 1
    if (aliceMeasurementsChoices[k] == 0 and bobMeasurementsChoices[k] == 2):
        if '00' in res:
            countA1B3[0] += 1
        if '01' in res:
            countA1B3[1] += 1
        if '10' in res:
            countA1B3[2] += 1
        if '11' in res:
            countA1B3[3] += 1
        normalizer += 1
        count13 += 1        
    if (aliceMeasurementsChoices[k] == 2 and bobMeasurementsChoices[k] == 0):
        if '00' in res:
            countA3B1[0] += 1
        if '01' in res:
            countA3B1[1] += 1
        if '10' in res:
            countA3B1[2] += 1
        if '11' in res:
            countA3B1[3] += 1
        normalizer += 1
        count31 += 1        
    if (aliceMeasurementsChoices[k] == 2 and bobMeasurementsChoices[k] == 2):
        if '00' in res:
            countA3B3[0] += 1
        if '01' in res:
            countA3B3[1] += 1
        if '10' in res:
            countA3B3[2] += 1
        if '11' in res:
            countA3B3[3] += 1
        normalizer += 1
        count33 += 1

# expected values of A1B1, A1B3, A3B1 and A3B3  measurements results
expect11 = (countA1B1[0]-countA1B1[1]-countA1B1[2]+countA1B1[3])/count11
expect13 = (countA1B3[0]-countA1B3[1]-countA1B3[2]+countA1B3[3])/count13
expect31 = (countA3B1[0]-countA3B1[1]-countA3B1[2]+countA3B1[3])/count31
expect33 = (countA3B3[0]-countA3B3[1]-countA3B3[2]+countA3B3[3])/count33

# CHSH correlation; must be equal to 2*sqrt(2) in the ideal case
corr = expect11 - expect13 + expect31 + expect33
diff = abs(corr - 2*math.sqrt(2))

## Print results

# CHSH inequality test
print('CHSH correlation value is ' + str(round(corr, 3)))
print('Difference from the ideal case is ' + str(round(diff, 3)) + '\n')

# Sifted key
print('Length of the sifted key is ' + str(siftedKeyLength))
print('Number of mismatching bits is ' + str(keyMismatchesNumber) + '\n')

# Errors of measurements
print('Number of errors of measurements is ' + str(errorCounter))
