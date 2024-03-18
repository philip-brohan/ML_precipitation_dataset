Visualizations - normalized precipitation stripes
=================================================

.. figure:: ../../visualizations/stripes/ERA5/total_precipitation_sample_11x13.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Normalized precipitation stripes from :doc:`ERA5 <stripes_ERA5>`. Smoothed with an 11x13 filter.

.. figure:: ../../visualizations/stripes/TWCR/PRATE_sample_11x13.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Same, but from :doc:`20CRv3 <stripes_TWCR>`.

.. figure:: ../../visualizations/stripes/CRU/Precip_sample_11x13.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Same, but from :doc:`CRU <stripes_CRU>`.

.. figure:: ../../visualizations/stripes/GPCC/in_situ/in_situ_sample_11x13.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Same, but from :doc:`GPCC <stripes_GPCC>`.

.. figure:: ../../visualizations/stripes/GPCP/Precip_sample_11x13.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Same, but from :doc:`GPCP <stripes_GPCP>`.


Script (`make_all_stripes.sh`) to regenerate all the stripes plots.

.. literalinclude:: ../../visualizations/stripes/make_all_stripes.sh
    :language: bash

The stripes creation scripts are organized by source:

.. toctree::
   :titlesonly:
   :maxdepth: 1

    ERA5 <stripes_ERA5>
    20CRv3 <stripes_TWCR>
    CRU <stripes_CRU>
    GPCC <stripes_GPCC>
    GPCP <stripes_GPCP>


