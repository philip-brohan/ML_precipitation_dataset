# Make tf.data.Datasets from ERA5 monthly precip

import os
import sys
import random
import tensorflow as tf
import numpy as np
import random

import specify


# Load a pre-standardised tensor from a list of files
def load_tensor(file_names):
    imta = []
    for file_name in file_names:
        sict = tf.io.read_file(file_name)
        imt = tf.io.parse_tensor(sict, np.float32)
        imta.append(tf.reshape(imt, [721, 1440, 1]))
    return tf.stack(imta, axis=2)


# Find out how many tensors available for each month from a source
def getDataAvailability(source):
    dir = "%s/MLP/normalised_datasets/%s" % (os.getenv("SCRATCH"), source)
    aFiles = os.listdir(dir)
    firstYr = 3000
    lastYr = 0
    maxCount = 0
    filesYM = {}
    for fN in aFiles:
        year = int(fN[:4])
        month = int(fN[5:6])
        if year < firstYr:
            firstYr = year
        if year > lastYr:
            lastYr = year
        key = "%04d%02d" % (year, month)
        if key not in filesYM:
            filesYM[key] = []
        else:
            filesYM[key].append("%s/%s" % (dir, fN))
        if len(filesYM[key]) > maxCount:
            maxCount = len(filesYM[key])
    return (firstYr, lastYr, maxCount, filesYM)


# Make a set of input filenames
def getFileNames(sources, purpose):
    avail = {}
    firstYr = specify.startYear
    lastYr = specify.endYear
    maxCount = 1
    for source in sources:
        avail[source] = getDataAvailability(source)
        if avail[source][0] > firstYr:
            firstYr = avail[source][0]
        if avail[source][1] < lastYr:
            lastYr = avail[source][1]
        if specify.correlatedEnsembles:
            maxCount = avail[source][2]  # always the same
        else:
            maxCount *= avail[source][2]

    # Make file name lists for available months - repeating if there are multiple ensemble members
    aMonths = []
    fNames = {}
    for rep in range(min(maxCount, specify.maxEnsembleCombinations)):
        for year in range(firstYr, lastYr + 1):
            for month in range(1, 13):
                mnth = "%04d%02d" % (year, month)
                smnth = []
                bad = False
                for source in sources:
                    if mnth in avail[source[3]]:
                        if specify.correlatedEnsembles:
                            smnth.append(source[3][mnth][rep])
                        else:
                            smnth.append(random.sample(source[3][mnth], 1))
                    else:
                        bad = True
                        break
                if bad:
                    continue
                mnth += "%05d" % rep
                aMonths.append(mnth)
                fNames[mnth] = smnth

    # Test/Train split
    if purpose is not None:
        test_ns = list(range(len(aMonths), specify.TestSplit))
        if purpose == "Train":
            aMonths = aMonths[~test_ns]
        elif purpose == "Test":
            aMonths = aMonths[test_ns]
        else:
            raise Exception("Unsupported purpose " + purpose)

    # Randomise the sequence of months
    aMonths = random.shuffle(aMonths)

    # Limit maximum data size
    if purpose == "Train" and specify.nTrainingMonths is not None:
        if len(aMonths) >= specify.nTrainingMonths:
            aMonths = aMonths[0 : specify.nTrainingMonths]
        else:
            raise ValueError(
                "Only %d months available, can't provide %d"
                % (len(aMonths), specify.nTrainingMonths)
            )
    if purpose == "Test" and specify.nTestMonths is not None:
        if len(aMonths) >= specify.nTestMonths:
            aMonths = aMonths[0 : specify.nTestMonths]
        else:
            raise ValueError(
                "Only %d months available, can't provide %d"
                % (len(aMonths), specify.nTestMonths)
            )
    # Return a list of lists of filenames
    result = []
    for key in aMonths:
        result.append(fNames[key])
    return result


# Get a dataset
def getDataset(inputSources, outputSources, purpose):
    # Get a list of filename sets
    inFiles = getFileNames(inputSources, purpose)

    # Create TensorFlow Dataset object from the source file names
    tnIData = tf.data.Dataset.from_tensor_slices(tf.constant(inFiles))

    # Create Dataset from the source file contents
    tsIData = tnIData.map(load_tensor, num_parallel_calls=tf.data.experimental.AUTOTUNE)

    if outputSources is not None:  # I.e. input and output are not the same
        outFiles = getFileNames(outputSources, purpose)
        tnOData = tf.data.Dataset.from_tensor_slices(tf.constant(outFiles))
        tsOData = tnOData.map(
            load_tensor, num_parallel_calls=tf.data.experimental.AUTOTUNE
        )

    # Zip the data together with the filenames (so we can find the date and source of each
    #   data tensor if we need it).
    if outputSources is not None:
        tz_data = tf.data.Dataset.zip((tnIData, tsIData, tsOData))
    else:
        tz_data = tf.data.Dataset.zip((tnIData, tsIData))

    # Optimisation
    if (purpose == "Train" and specify.trainCache) or (
        purpose == "Test" and specify.testCache
    ):
        tz_data = tz_data.cache()  # Great, iff you have enough RAM for it

    tz_data = tz_data.prefetch(tf.data.experimental.AUTOTUNE)

    return tz_data
