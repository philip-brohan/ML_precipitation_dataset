#!/bin/bash

echo -n '' > mnth.txt

for var in PRMSL TMP2m PRATE SST
do

    # Initial minimal make to create the zarr structure (hence --delete)
    ./make_all_tensors.py --variable=$var --month=3 --day=12 --hour=6 --delete

    # Then parallelize by months
    for month in {1..12}
    do
        for hour in $(seq 0 3 24)
        do
            echo "./make_all_tensors.py --variable=$var --month=$month --hour=$hour" >> mnth.txt
        done
    done

done 

cat mnth.txt | spice_parallel --time=59
rm mnth.txt
