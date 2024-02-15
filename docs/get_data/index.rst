Get the data to be used
=======================

We are interested in historical monthly average precipitation over long timescales (decades to centuries). So we are going to look at various different sources of such data:

* Two reanalyses:
   * `ERA5 <https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5>`_ - a full-input reanalysis which should give good estimates, but will have large inhomogeneities as satellite inputs change.
   * `20CRv3 <https://www.esrl.noaa.gov/psd/data/20thC_Rean/>`_ - a reanalysis which assimilates only surface pressure observations. Probably less precise, but will have fewer inhomogeneities. Also gives us an estimate of precipitation that is independent of precipitation observations
   The reanalyses give us other variables (temperature and pressure as well as precipitation).
* Two observational datasets:
   * `GPCC <https://www.dwd.de/EN/ourservices/gpcc/gpcc.html>`_
   * `CRU <https://crudata.uea.ac.uk/cru/data/hrg/>`_
   These are based *only* on land precipitation observations, and only give estimates over land.
* A blended dataset:
   * `GPCP <https://www.esrl.noaa.gov/psd/data/gridded/data.gpcp.html>`_
   This is a blend of satellite and rain gauge data, gives global (land and sea) estimates, but is particularly susceptible to inhomogeneities from changing input sources.

That gives us five different datasets, each with its own strengths and weaknesses. We will use them to compare the different estimates of precipitation, and to look at the long-term trends in precipitation. For each dataset we have a separate page with instructions on how to download and access the data.

.. toctree::
   :titlesonly:
   :maxdepth: 1

   Download and access ERA5 data <ERA5>
   Download and access 20CR data <20CR>
   Download and access GPCC data <GPCC>
   Download and access CRU data <CRU>
   Download and access GPCP data <GPCP>

We also want a land-sea mask (for plotting only). We will use a land-surface only variable from ERA5-land for this (we only need one month). If we needed it to model the data it would be necessary to choose a land-mask that matched the data resolution and grid, but for plotting purposes we can use anything.

.. toctree::
   :titlesonly:
   :maxdepth: 1

   Download the land mask <land_mask>

Convenience script to download all the data:

.. literalinclude:: ../../get_data/download_all_data.sh


