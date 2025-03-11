#!/bin/bash

# Add metadata to the hourly raw tensor zarr files
# Requires raw tensors


(cd TWCR && ./update_tensor_metadata.py --variable=TMP2m)
(cd TWCR && ./update_tensor_metadata.py --variable=SST)
(cd TWCR && ./update_tensor_metadata.py --variable=PRMSL)
(cd TWCR && ./update_tensor_metadata.py --variable=PRATE)

