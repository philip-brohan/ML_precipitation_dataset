How homogenous is ERA5?
=========================

:doc:`20CRv3 is reasonably homogenous back to about 1950 </20CRv3_homogeneity>`- ERA5 only goes back to 1940, but we can't expect it to be homogenous, because it assimilates a much larger and more changeable set of observations. We can look at the homogeneity of ERA5 by making :doc:`normalized <normalization/index>` extended-stripes plots of the :doc:`variables of interest <get_data/index>`:

Total precipitation
-------------------

.. figure:: images/ERA5_stripes/total_precipitation.webp
   :width: 95%
   :align: center
   :figwidth: 100%

2m temperature
--------------

.. figure:: images/ERA5_stripes/2m_temperature.webp
   :width: 95%
   :align: center
   :figwidth: 100%

Mean sea level pressure
-----------------------

.. figure:: images/ERA5_stripes/mean_sea_level_pressure.webp
   :width: 95%
   :align: center
   :figwidth: 100%


10m u component of wind
-----------------------

.. figure:: images/ERA5_stripes/10m_u_component_of_wind.webp
   :width: 95%
   :align: center
   :figwidth: 100%


10m v component of wind
-----------------------

.. figure:: images/ERA5_stripes/10m_v_component_of_wind.webp
   :width: 95%
   :align: center
   :figwidth: 100%


2m relative humidity
--------------------

.. figure:: images/ERA5_stripes/2m_relative_humidity.webp
   :width: 95%
   :align: center
   :figwidth: 100%

Unsurprisingly, ERA5 shows strong inhomogeneities: Two big changes occur in about 1980 and about 1998. The former produces a global change in precipitation, and is probably caused by the assimilation of `MSU satellite observations <https://en.wikipedia.org/wiki/Microwave_sounding_unit>`_; the second is concentrated in the tropics and is probably caused by the assimilation of `TRMM satellite observations <https://en.wikipedia.org/wiki/ Tropical_Rainfall_Measuring_Mission>`_.