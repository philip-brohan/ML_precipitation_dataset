Visualizations - normalized pressure stripes
============================================

.. figure:: ../../visualizations/stripes/ERA5/mean_sea_level_pressure_sample_11x13.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Normalized temperature stripes from :doc:`ERA5 <stripes_ERA5>`. Smoothed with an 11x13 filter.

.. figure:: ../../visualizations/stripes/TWCR/PRMSL_sample_11x13.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Same, but from :doc:`20CRv3 <stripes_TWCR>`.


Script (`make_all_stripes.sh`) to regenerate all the stripes plots.

.. literalinclude:: ../../visualizations/stripes/make_all_stripes.sh
    :language: bash

The stripes creation scripts are organized by source:

.. toctree::
   :titlesonly:
   :maxdepth: 1

    ERA5 <stripes_ERA5>
    20CRv3 <stripes_TWCR>


