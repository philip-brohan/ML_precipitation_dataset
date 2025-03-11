#!/bin/bash

# Make all the raw tensors
# Requires downloaded data

(cd TWCR && ./make_all_tensors.py --variable=TMP2m)
(cd TWCR && ./make_all_tensors.py --variable=SST)
(cd TWCR && ./make_all_tensors.py --variable=PRMSL)
(cd TWCR && ./make_all_tensors.py --variable=PRATE)

