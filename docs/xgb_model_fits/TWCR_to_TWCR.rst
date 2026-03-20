Fitting an XGBoost model to the TWCR data
=========================================


.. figure:: ../images/XGB_TWCR/test_train.webp
   :width: 95%
   :align: center
   :figwidth: 100%

   Validation plots for an XGBoost model trained to predict precipitation from a set of surface variables (temperature, humidity, pressure, latitude, longitude, calendar month). Left scatter plot shows performance on the training dataset, right scatter plot shows performance on the test dataset. (`Figure source <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/ML_models/xgb_monthly/validate_2.py>`_).


.. figure:: ../images/XGB_TWCR/monthly.webp
   :width: 95%
   :align: center
   :figwidth: 100%

   Precipitation field for one month as reconstructed by the model. (`Figure source <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/ML_models/xgb_monthly/validate_month.py>`_).
 

.. figure:: ../images/XGB_TWCR/None_area_039.webp
   :width: 95%
   :align: center
   :figwidth: 100%

   Global mean precipitation time-series as predicted by the model. (`Figure source <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/ML_models/xgb_monthly/time_series/plot_ts_validation.py>`_).
 

.. figure:: ../images/XGB_TWCR/3_stripes_sample_11x13.webp
   :width: 95%
   :align: center
   :figwidth: 100%

   Extended-stripes plots of precipitation. Top row - target (TWCR precipitation), middle row - model prediction, bottom row - difference (`Figure source <https://github.com/philip-brohan/ML_precipitation_dataset/blob/f30502ac9296f4b88c18562c1e635a4572b0c375/ML_models/xgb_monthly/stripes/stripes_triple.py>`_).
 

