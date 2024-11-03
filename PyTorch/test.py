#!/bin/python

import torch
if torch.backends.mps.is_available():
    mps_device = torch.device("mps")
    x = torch.ones(1, device=mps_device)
    print (x)
    print(torch.backends.mps.is_available()) 
    print(torch.backends.mps.is_built())
else:
    print ("MPS device not found.")