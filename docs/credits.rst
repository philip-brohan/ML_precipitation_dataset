Authors and acknowledgements
----------------------------

This document is currently maintained by `Philip Brohan <https://brohan.org>`_ (philip.brohan @ metoffice.gov.uk). All criticism should be directed to him - put please **don't** send email, `raise an issue <https://github.com/philip-brohan/ML_precipitation_dataset/issues/new>`_ instead.

|

All blame should go to the maintainer; credit is more widely distributed:

* This document was written by `Philip Brohan  <https://brohan.org>`_ (Met Office). He was supported by the Met Office Hadley Centre Climate Programme funded by BEIS, and by the Met Office Weather and Climate Science for Service Partnership (WCSSP) South Africa as part of the Newton Fund.
  
* This work follows on from `previous work on climate modelling and data assimilation with ML <https://brohan.org/Proxy_20CR/>`_.
 
* The `XGBoost <https://xgboost.readthedocs.io/en/stable/>`_ library is used to train the decision tree models.
* The `TensorFlow <https://www.tensorflow.org/>`_ library is used for efficient data handling.
  
* Training data used came from: 

  * The `ERA5 reanalysis <https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5>`_ 
  * The `20th Century Reanalysis (version 3) <https://www.esrl.noaa.gov/psd/data/20thC_Rean/>`_ 
  * `CRU TS <https://crudata.uea.ac.uk/cru/data/hrg/>`_
  * `GPCC <https://www.esrl.noaa.gov/psd/data/gridded/data.gpcc.html>`_
  * `GPCP <https://www.esrl.noaa.gov/psd/data/gridded/data.gpcp.html>`_
  
* Much of the data used was obtained from the Copernicus `Climate Change Service Climate Data Store <https://cds.climate.copernicus.eu>`_. 

* This work benefited from AI assistance: Both `Github Copilot <https://github.com/features/copilot>`_ and `ChatGPT <https://chat.openai.com/>`_ were used to help write the code and documentation. In spite of this, the authors and maintainer are responsible for the entirety of the result.

* The calculations here make extensive use of `GNU Parallel <https://www.gnu.org/software/parallel/>`_ (`Tange 2011 <https://www.usenix.org/publications/login/february-2011-volume-36-number-1/gnu-parallel-command-line-power-tool>`_).
 
* This software is written in `python <https://www.python.org/>`_, in an environment configured with `conda <https://docs.conda.io/en/latest/>`_.

* The code and documentation use `git <https://git-scm.com/>`_ and `GitHub <https://github.com/>`_. The documentation is written with `sphinx <https://www.sphinx-doc.org/en/master/index.html>`_.

Note that appearance on this list does not mean that the person or organization named endorses this work, agrees with any of it, or even knows of its existence.
