# Make tf.data.Datasets from from normalised data in zarr files

# This is a generic script to make a TensorFlow Dataset
# Follow the instructions in autoencoder.py to use it.

import os
import sys
import tensorflow as tf
import numpy as np
import random
import zarr
import tensorstore as ts


# Find out what data are available from a source
def getDataAvailability(source):
    zfile = "%s/MLP/normalized_datasets/%s_zarr" % (
        os.getenv("SCRATCH"),
        source,
    )
    zarr_array = zarr.open(zfile, mode="r")
    AvailableMonths = zarr_array.attrs["AvailableMonths"]
    return AvailableMonths


# Make a set of months available in all of a set of sources
def getMonths(
    input_sources,
    output_sources,
    purpose,
    firstYr,
    lastYr,
    testSplit,
    maxTrainingMonths,
    maxTestMonths,
):
    sources = input_sources
    if output_sources is not None:
        sources = sources + output_sources
        sources = list(set(sources))  # Unique sources
    avail = {}
    months_in_all = None
    for source in sources:
        avail[source] = getDataAvailability(source)
        if months_in_all is None:
            months_in_all = set(
                [x[:7] for x in avail[source].keys()]
            )  # Unique year-month
        else:
            months_in_all = months_in_all.intersection(
                set([x[:7] for x in avail[source].keys()])
            )

    # Filter by range of years
    filtered = []
    for month in months_in_all:
        year = int(month[:4])
        if (firstYr is None or year >= firstYr) and (lastYr is None or year <= lastYr):
            filtered.append(month)
    months_in_all = filtered

    months_in_all.sort()  # Months in time order (validation plots)

    # Test/Train split
    if purpose is not None:
        test_ns = list(range(0, len(months_in_all), testSplit))
        if purpose == "Train":
            months_in_all = [
                months_in_all[x] for x in range(len(months_in_all)) if x not in test_ns
            ]
        elif purpose == "Test":
            months_in_all = [
                months_in_all[x] for x in range(len(months_in_all)) if x in test_ns
            ]
        else:
            raise Exception("Unsupported purpose " + purpose)

    # Limit maximum data size
    if purpose == "Train" and maxTrainingMonths is not None:
        if len(months_in_all) >= maxTrainingMonths:
            months_in_all = months_in_all[0:maxTrainingMonths]
        else:
            raise ValueError(
                "Only %d months available, can't provide %d"
                % (len(months_in_all), maxTrainingMonths)
            )
    if purpose == "Test" and maxTestMonths is not None:
        if len(months_in_all) >= maxTestMonths:
            months_in_all = months_in_all[0:maxTestMonths]
        else:
            raise ValueError(
                "Only %d months available, can't provide %d"
                % (len(months_in_all), maxTestMonths)
            )

    # months in all is a list of yyyy-mm strings - one for each month with data
    #  present in all the sources
    # avail is a list of dictionaries - one for each source - mapping the yyyy-mm(_mm) strings to date indices
    return months_in_all, avail


# Get a dataset
def getDataset(specification, purpose):
    # Get a list of months to use
    inMonths, inIndices = getMonths(
        specification["inputTensors"],
        specification["outputTensors"],
        purpose,
        specification["startYear"],
        specification["endYear"],
        specification["testSplit"],
        specification["maxTrainingMonths"],
        specification["maxTestMonths"],
    )

    # Create TensorFlow Dataset object from the date strings
    tnIData = tf.data.Dataset.from_tensor_slices(tf.constant(inMonths))

    # Open all the source tensorstores
    tsa_in = {}
    for source in specification["inputTensors"]:
        zfile = "%s/MLP/normalized_datasets/%s_zarr" % (
            os.getenv("SCRATCH"),
            source,
        )
        tsa_in[source] = ts.open(
            {
                "driver": "zarr",
                "kvstore": "file://" + zfile,
            }
        ).result()

    # Map functions to get tensors from date strings and date indices
    #  use a random ensemble member, if there is more than one
    def load_input_tensors_from_month_py(month):
        mnth = month.numpy().decode("utf-8")
        source = specification["inputTensors"][0]
        tsa = tsa_in[source]
        try:  # Assume no ensemble
            idx = inIndices[source][mnth]
            ima = tf.convert_to_tensor(tsa[:, :, idx].read().result(), tf.float32)
        except KeyError:  # Ensemble
            m_idx = random.randint(0, 9)  # Random member
            idx = inIndices[source]["%s_%02d" % (mnth, m_idx)]
            ima = tf.convert_to_tensor(
                tsa[:, :, m_idx, idx].read().result(), tf.float32
            )
        ima = tf.reshape(ima, [721, 1440, 1])
        for fni in range(1, len(specification["inputTensors"])):
            source = specification["inputTensors"][fni]
            tsa = tsa_in[source]
            try:  # Assume no ensemble
                idx = inIndices[source][mnth]
                imt = tf.convert_to_tensor(tsa[:, :, idx].read().result(), tf.float32)
            except KeyError:  # Ensemble
                m_idx = random.randint(0, 9)  # Random member
                idx = inIndices[source]["%s_%02d" % (mnth, m_idx)]
                imt = tf.convert_to_tensor(
                    tsa[:, :, m_idx, idx].read().result(), tf.float32
                )
            imt = tf.reshape(ima, [721, 1440, 1])
            ima = tf.concat([ima, imt], 2)
        return ima

    def load_input_tensor(month):
        result = tf.py_function(
            load_input_tensors_from_month_py,
            [month],
            tf.float32,
        )
        return result

    # Create Dataset from the source file contents
    tsIData = tnIData.map(
        load_input_tensor, num_parallel_calls=tf.data.experimental.AUTOTUNE
    )

    if specification["outputTensors"] is not None:
        tsa_out = {}
        for source in specification["outputTensors"]:
            zfile = "%s/MLP/normalized_datasets/%s_zarr" % (
                os.getenv("SCRATCH"),
                source,
            )
            tsa_out[source] = ts.open(
                {
                    "driver": "zarr",
                    "kvstore": "file://" + zfile,
                }
            ).result()

        def load_output_tensors_from_month_py(month):
            mnth = month.numpy().decode("utf-8")
            source = specification["outputTensors"][0]
            tsa = tsa_out[source]
            try:  # Assume no ensemble
                idx = inIndices[source][mnth]
                ima = tf.convert_to_tensor(tsa[:, :, idx].read().result(), tf.float32)
            except KeyError:  # Ensemble
                m_idx = random.randint(0, 9)  # Random member
                idx = inIndices[source]["%s_%02d" % (mnth, m_idx)]
                ima = tf.convert_to_tensor(
                    tsa[:, :, m_idx, idx].read().result(), tf.float32
                )
            ima = tf.reshape(ima, [721, 1440, 1])
            for fni in range(1, len(specification["outputTensors"])):
                source = specification["outputTensors"][fni]
                tsa = tsa_out[source]
                try:  # Assume no ensemble
                    idx = inIndices[source][mnth]
                    imt = tf.convert_to_tensor(
                        tsa[:, :, idx].read().result(), tf.float32
                    )
                except KeyError:  # Ensemble
                    m_idx = random.randint(0, 9)  # Random member
                    idx = inIndices[source]["%s_%02d" % (mnth, m_idx)]
                    imt = tf.convert_to_tensor(
                        tsa[:, :, m_idx, idx].read().result(), tf.float32
                    )
                imt = tf.reshape(imt, [721, 1440, 1])
                ima = tf.concat([ima, imt], 2)
            return ima

        def load_output_tensor(month):
            result = tf.py_function(
                load_output_tensors_from_month_py,
                [month],
                tf.float32,
            )
            return result

        tsOData = tnIData.map(
            load_output_tensor, num_parallel_calls=tf.data.experimental.AUTOTUNE
        )

    # Zip the data together with the filenames (so we can find the date and source of each
    #   data tensor if we need it).
    if specification["outputTensors"] is not None:
        tz_data = tf.data.Dataset.zip((tnIData, tsIData, tsOData))
    else:
        tz_data = tf.data.Dataset.zip((tnIData, tsIData))

    # Optimisation
    if (purpose == "Train" and specification["trainCache"]) or (
        purpose == "Test" and specification["testCache"]
    ):
        tz_data = tz_data.cache()  # Great, iff you have enough RAM for it

    tz_data = tz_data.prefetch(tf.data.experimental.AUTOTUNE)

    return tz_data
