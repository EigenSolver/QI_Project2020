#!/usr/bin/env python
# coding: utf-8

# In[26]:


import logging
import os
from getpass import getpass

from quantuminspire.credentials import load_account, get_token_authentication, get_basic_authentication
from quantuminspire.api import QuantumInspireAPI
# from quantuminspire.projectq.backend_qx import QIBackend

import numpy as np
import pandas as pd


# In[ ]:


get_ipython().run_line_magic('env', 'QI_EMAIL=')
get_ipython().run_line_magic('env', 'QI_PASSWORD=')


# In[59]:


email = os.getenv('QI_EMAIL') 
password = os.getenv('QI_PASSWORD')
server_url = r'https://api.quantum-inspire.com'

token = load_account()
if token is not None:
    authentication = get_token_authentication(token)
else:
    authentication = get_basic_authentication(email, password)

qi = QuantumInspireAPI(server_url, authentication)


# In[60]:


def sphere_meshing(n_θ, n_ϕ):
    '''
    n_θ: partition number for polar angle
    n_ϕ: partition number for azimuthal angle
    '''
    coords=[]
    set_θ=np.linspace(0,np.pi,n_θ)
    set_ϕ=np.linspace(0,2*np.pi,n_ϕ)
    for θ in set_θ:
        for ϕ in set_ϕ:
            coords.append((θ,ϕ))
    return coords


# In[61]:


def parameterized_QACM(loc):
    θ,ϕ=loc
    qasm = '''
    version 1.0

    qubits 5

    # initialize the state
    prep_z q[2]
    Ry q[2], {0}
    Rz q[2], {1}
    

    #preparation
    Ry q[0], 1.107149
    #rewrite CNOT q[0],q[4] and CNOT q[4],q[0] usign nearest neighbors
    SWAP q[0],q[2] 
    CNOT q[2],q[4]

    Ry q[4], 0.729728
    CNOT q[4],q[2]
    SWAP q[0],q[2]

    Ry q[0], 0.463648

    #copying
    CNOT q[2], q[0]
    CNOT q[2], q[4]
    CNOT q[0], q[2]
    CNOT q[4], q[2]

    #Rotate back and measure
    Rz q[2], {2}
    Ry q[2], {3}
    Measure_z q[0]
    '''
    return qasm.format(θ,ϕ,-ϕ,-θ)


# In[73]:


# evenly mesh the sphere, set parameter
n_theta=10
n_phi=20
N_shots=2048

target_points=np.array(sphere_meshing(n_theta,n_phi))
# save the data, optional
np.savetxt("target_points.csv",target_points)


# In[ ]:


# iterate over the sphere, run task
N=n_theta*n_phi
backend_type = qi.get_backend_type_by_name('Starmon-5')

copied_data=[]
for points in target_points:
    qasm=parameterized_QACM(points)
    result = qi.execute_qasm(qasm, backend_type=backend_type, number_of_shots=N_shots)
    hist=result.get('histogram', {})
    copied_data.append([hist["0"],hist["1"]])
copied_data=np.array(copied_data)


# In[ ]:


data_sheet=pd.DataFrame(data=np.hstack((target_points,copied_data)),columns=["θ","ϕ","prob_0","prob_1"])


# In[ ]:


data_sheet.head()


# In[ ]:


# save to excel, optional
data_sheet.to_excel("data_sheet.xlsx")

