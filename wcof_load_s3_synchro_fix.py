import xarray as xr
import numpy as np
from scipy.interpolate import griddata
import pandas as pd
import datetime as dt
import time, scipy.io
# load the amazon s3 file system access module
import s3fs
from pyproj import Geod
import pdb
#
# atime is now, thedays
#
fs=s3fs.S3FileSystem(anon=True)
def wcof_load_s3_synchro_fix(atime): # don't need offset, numbs, my or my1
    io=0
    ioerr=0
    # this goes upto 3 days behind current time
    urlpre='s3://noaa-nos-ofs-pds/wcofs/netcdf/'
    # below is the string for full 3-d data but we only want 2-d data here.
    #filestr='nos.wcofs.fields.'
    filestr='nos.wcofs.2ds.'
    filepost='.t03z.nc'
    # we have an issue that nos.wcofs.2ds.n001.20220913.t03z.nc is not at time 001 but at time 2022-09-13T04:00:00
    #
    # compute the parts so we can construct the url and filename
    #
    year=atime.year
    month=atime.month
    day=atime.day
    # print date of files retrieving so we can keep track of where we are.
    print(str(year)+'/'+str(month)+'/'+str(day))
    # okay now we have year month and day of our offset date so we want to find the hour 1 to hour 24 values
    datetoget=dt.datetime(year,month,day)
    # so datetoget is the date we want to get but to get the actual hours for that day we need to get 3 hours earlier
    # set up appropiate loop?
    thehours=np.arange(1,73,1)
    # set up to read forecast files
    forns='f'
	# loop through the hours we want to load    
    for zhours in thehours:
    	# set up strings for filename formation
        syear=str(year)
        if month < 10:
            smonth='0'+str(month)
        else:
            smonth=str(month)
        if day < 10:
            sday='0'+str(day)
        else:
            sday=str(day)
        if zhours < 10:
            forehour=forns+'00'+str(zhours)
        else:
            forehour=forns+'0'+str(zhours)
        # This is for the Amazon s3 site
        urlstr=urlpre+syear+smonth+'/'+filestr+forehour+'.'+syear+smonth+sday+filepost
        # show the filename string we are trying to load
        print(urlstr)
        # open the file on S3
        fileid=fs.open(urlstr)
        # read the file
        dataset=xr.open_dataset(fileid)
        # close the file so nothing bad happens
        fileid.close()
        # extract variables for plotting purposes
        lat_r=dataset['lat_rho']
        lon_r=dataset['lon_rho']
        lat_v=dataset['lat_v'].values
        lon_v=dataset['lon_v'].values
        lat_u=dataset['lat_u'].values
        lon_u=dataset['lon_u'].values       
        #
        # get the file/data time
        #
        otime=dataset['ocean_time']
        roms_tauy=dataset['svstr']
        roms_taux=dataset['sustr']
        roms_f=dataset['f']
        roms_fg=dataset['f']
        roms_rho=dataset['rho0']
        roms_zeta=dataset['zeta']
        roms_zeta=np.squeeze(roms_zeta)
        roms_tauy=np.squeeze(roms_tauy)
        roms_taux=np.squeeze(roms_taux)
        roms_f=roms_f[0:-1,:]
        tauy=roms_tauy.values
        taux=roms_taux.values
        f=roms_f.values
        # set up for gradients
        dtaux=taux[0:-1,:]-taux[1:,:]
        dtauy=tauy[:,0:-1]-tauy[:,1:]
        # set up information for geographical plotting
        g=Geod(ellps='WGS84')
        az1,az2,dx=g.inv(lon_v[:,0:-1],lat_v[:,0:-1],lon_v[:,1:],lat_v[:,1:])
        az3,az4,dy=g.inv(lon_u[0:-1,:],lat_u[0:-1,:],lon_u[1:,:],lat_u[1:,:])
        # set up parameters for Ekman upwelling computation
        f=0.86e-4
        rhof=1/(roms_rho*f)
        rhof=rhof.to_numpy()
        # compute Ekman upwelling.
        we=rhof*(dtauy/dx-dtaux/dy)
        # longitude corresponds to dimension 1
        # latitude correponds to dimension 0
        dzeta=(roms_zeta[0:-1,:]-roms_zeta[1:,:])
        az5,az6,dyr=g.inv(lon_r[0:-1,:],lat_r[0:-1,:],lon_r[1:,:],lat_r[1:,:])
        dzetady=-1.0*dzeta/dyr
        ugeo=dzetady/f
        ugeo=ugeo*9.8
        % get the temperature
        roms_temp = dataset['temp_sur']
        roms_time = dataset['ocean_time']
        if io==0:
            bigtemp=np.expand_dims(we,axis=0)
            bigugeo=np.expand_dims(ugeo,axis=0)
            bigsfctemp=roms_temp
            bigtime=otime
            io=1
        else:
            bigtime=np.append(bigtime,otime)
            btmp=np.expand_dims(we,axis=0)
            utmp=np.expand_dims(ugeo,axis=0)
            bigtemp=np.vstack((bigtemp,btmp))
            bigugeo=np.vstack((bigugeo,utmp))
            bigsfctemp=np.vstack((bigsfctemp,roms_temp))
    if ioerr==0:
        return [bigtime, bigtemp, bigugeo, bigsfctemp,lat_u,lon_u,lat_v,lon_v,lat_r,lon_r]
    else:
        return 1
