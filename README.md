Code to create Synchro upwelling plots estimated from the WCOFS model forecast output.
Currently this code only uses the 4km WCOFS and is limited to the area around Monterey Bay.

The code reads the WCOFS model from the NOAA S3 instance.  In particular it only reads the 2d data.
The 2-d data has hourly forecast data.  The full fields data is only output every 3 hours, so we didn't use that data (it would also take a long time to load).
The code uses the wind stress components to estimate ekman upwelling.
The u-component of the geostrophic upwelling is also computed.
The third panel of the plot contains the sea surface temperature.
