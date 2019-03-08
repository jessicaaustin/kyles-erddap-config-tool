To generate these datasets:

1. Datasets at http://erddap.sensors.axds.co/erddap/index.html are already following IOOS metadata profile 1.2. 
So step one is to export one of these. To do this, find a dataset and export it as `.nc` file type.

1. Cleanup the nc file. 
    
    ```bash
    # this is an example; replace morro-bay-bs1-met with your dataset name, and use the appropriate vars
    
    # rename row to time
    ncrename -h -d row,time morro-bay-bs1-met.nc
    
    # for some reason it creates a bunch of `*_strlen` variables. average those out
    # ref: https://sourceforge.net/p/nco/discussion/9830/thread/3d35b42d/
    ncwa -h -C \
       -v air_pressure,air_pressure_qc_agg,air_pressure_qc_tests,air_temperature,air_temperature_qc_agg,air_temperature_qc_tests,dew_point_temperature,dew_point_temperature_qc_agg,dew_point_temperature_qc_tests,latitude,longitude,precipitation_increment_cm_time__mean_over_pt2m,precipitation_increment_cm_time__mean_over_pt2m_qc_agg,precipitation_increment_cm_time__mean_over_pt2m_qc_tests,relative_humidity,relative_humidity_qc_agg,relative_humidity_qc_tests,solar_radiation,solar_radiation_qc_agg,solar_radiation_qc_tests,station,time,wind_chill_temperature,wind_chill_temperature_qc_agg,wind_chill_temperature_qc_tests,wind_from_direction,wind_from_direction_qc_agg,wind_from_direction_qc_tests,wind_speed,wind_speed_qc_agg,wind_speed_qc_tests,z \
       -a air_pressure_qc_tests_strlen,air_temperature_qc_tests_strlen,dew_point_temperature_qc_tests_strlen,precipitation_increment_cm_time__mean_over_pt2m_qc_tests_strlen,relative_humidity_qc_tests_strlen,solar_radiation_qc_tests_strlen,station_strlen,wind_chill_temperature_qc_tests_strlen,wind_from_direction_qc_tests_strlen,wind_speed_qc_tests_strlen \
       morro-bay-bs1-met.nc out.nc
    ```

1. Upload the nc file to gluster at `/mnt/store/data/sensors/ioos_gold_standard/`

1. Generate the dataset xml using `GenerateDatasetsXml.sh` (see main README)

1. Modify the generated dataset xml: remove the `addAttributes` section. 

1. Add the dataset xml to the list here.

