Code to create Synchro upwelling plots estimated from the WCOFS model forecast output.
Currently this code only uses the 4km WCOFS and is limited to the area around Monterey Bay.

The code reads the WCOFS model from the NOAA S3 instance.  In particular it only reads the 2d data.
The 2-d data has hourly forecast data.  The full fields data is only output every 3 hours, so we didn't use that data (it would also take a long time to load).
The code uses the wind stress components to estimate ekman upwelling.
The u-component of the geostrophic upwelling is also computed.
The third panel of the plot contains the sea surface temperature.

How the code is run:
wcof_get_s3_synchro_30day.py calls wcof_load_s3_synchro30day.py
The above code creates the image files for the movie as a series of png files.  These are written to a disk mounted to a VM.
upwellmovie.py uses a copy of gm convert to create the animated gif with a 2 second delay between images.
The movie file is then scp'd from one VM to another that has access to the webserver.  (file_push.py)
A perl script copies the movie file on a regular interval from the VM to the webserver VM. (copytoSERVER.perl)
Where the SERVER name is replaced with the actual server name.
