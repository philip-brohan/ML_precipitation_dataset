#!/bin/bash

# Make all the normalized tensors
# Requires pre-made normalization parameters.


(cd TWCR_tf_MM && ./make_all_tensors.py --variable=TMP2m)
(cd TWCR_tf_MM && ./make_all_tensors.py --variable=SST)
(cd TWCR_tf_MM && ./make_all_tensors.py --variable=PRMSL)
(cd TWCR_tf_MM && ./make_all_tensors.py --variable=PRATE)

