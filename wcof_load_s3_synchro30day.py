import xarray as xr
import numpy as np
from scipy.interpolate import griddata
import pandas as pd
import datetime as dt
import time, scipy.io
#from urllib.error import HTTPError
#import matplotlib.pyplot as plt
import s3fs
from pyproj import Geod
import pdb
#
# atime is now, thedays
fs=s3fs.S3FileSystem(anon=True)
def wcof_load_s3_synchro30day(atime): # don't need offset, numbs, my or my1
#def wcof_load_s3_synchro(atime,offset,numbs,mx,my):
    io=0
    ioerr=0
    # this goes upto 3 days behind current time
    urlpre='s3://noaa-nos-ofs-pds/wcofs/netcdf/'
    #filestr='nos.wcofs.fields.'
    filestr='wcofs.t03z.'
    filepost='.2ds.'
    #filestr='nos.wcofs.2ds.'
    #filepost='.t03z.nc'
    # we have an issue that nos.wcofs.2ds.n001.20220913.t03z.nc is not at time 001 but at time 2022-09-13T04:00:00
    #
    backtime=np.arange(30,-1,-1)
    #backtime=np.arange(2,-1,-1)
    for ii in backtime:
        offset=ii
    #offset=30
        thedate=atime-dt.timedelta(days=int(offset))
    # compute the parts so we can construct the url and filename
        startyear=thedate.year
        startmonth=thedate.month
        startday=thedate.day
    #
        cyear=atime.year
        cmonth=atime.month
        cday=atime.day
        
        year=thedate.year
        month=thedate.month
        day=thedate.day
   
        print(str(year)+'/'+str(month)+'/'+str(day))
    #pdb.set_trace()
    # okay now we have year month and day of our offset date so we want to find the hour 1 to hour 24 values
        datetoget=dt.datetime(year,month,day)
        currentdate=dt.datetime(cyear,cmonth,cday)
        if datetoget==currentdate:
            numbs=72
        else:
            numbs=24
    
    # so datetoget is the date we want to get but to get the actual hours for that day we need to get 3 hours earlier
#    astart_date=datetoget-dt.timedelta(hours=3)
    # set up appropiate loop?
    #thehours=np.arange(3,75,3)
    #thehours=np.arange(1,73,1)
    #thehours=np.arange(1,11,1)
    #forns='f'
        if numbs > 24:
            thehours=np.arange(1,73,1)
            forns='f'
        else:
            thehours=np.arange(1,25,1)
            forns='n'
    
        for zhours in thehours:
        # compute offset from start
            if zhours==24 and forns=='n':
                timetoget=datetoget
                year=timetoget.year
                month=timetoget.month
                day=timetoget.day
                hour=24
            else:
                if forns=='n':
                    timetoget=datetoget+dt.timedelta(hours=int(zhours))
                    hour=timetoget.hour
                else:
                    timetoget=datetoget
                    hour=zhours
            #timetoget=astart_date+dt.timedelta(hours=int(zhours))
                year=timetoget.year
                month=timetoget.month
                day=timetoget.day
                #hour=timetoget.hour
        # case to get 24 hr values and not have n000 or f000 since we have n024 and f024
            #if hour==0:
            #    timetoget=datetoget+dt.timedelta(hours=int(zhours-1))
            #    year=timetoget.year
            #    month=timetoget.month
            #    day=timetoget.day
            #    hour=24
        # end if    
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
        #urlstr=urlpre+syear+smonth+'/'+filestr+syear+smonth+sday+filepost+forehour+'.nc'
            urlstr=urlpre+syear+'/'+smonth+'/'+sday+'/'+filestr+syear+smonth+sday+filepost+forehour+'.nc'
        #urlstr=urlpre+syear+smonth+'/'+filestr+forehour+'.'+syear+smonth+sday+filepost
            print(urlstr)
        #pdb.set_trace()
            fileid=fs.open(urlstr)
            dataset=xr.open_dataset(fileid)
        #fileid.close()
        #pdb.set_trace()
            lat_r=dataset['lat_rho']
            lon_r=dataset['lon_rho']
            lat_v=dataset['lat_v'].values
            lon_v=dataset['lon_v'].values
            lat_u=dataset['lat_u'].values
            lon_u=dataset['lon_u'].values
        
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
        #pdb.set_trace()
            dtaux=taux[0:-1,:]-taux[1:,:]
            dtauy=tauy[:,0:-1]-tauy[:,1:]
        #dy=lat_u[0:-1,:]-lat_u[1:,:]*111000
            g=Geod(ellps='WGS84')
            az1,az2,dx=g.inv(lon_v[:,0:-1],lat_v[:,0:-1],lon_v[:,1:],lat_v[:,1:])
            az3,az4,dy=g.inv(lon_u[0:-1,:],lat_u[0:-1,:],lon_u[1:,:],lat_u[1:,:])
            f=0.86e-4
            rhof=1/(roms_rho*f)
            rhof=rhof.to_numpy()
        #pdb.set_trace()
            we=rhof*(dtauy/dx-dtaux/dy)
        #uek=tauy/(f*roms_rho.values)
        #vek=taux/(f*roms_roh.values)
        # longitude corresponds to dimension 1
        # latitude correponds to dimension 0
            dzeta=(roms_zeta[0:-1,:]-roms_zeta[1:,:])
            az5,az6,dyr=g.inv(lon_r[0:-1,:],lat_r[0:-1,:],lon_r[1:,:],lat_r[1:,:])
        #dy=(lat_r[0:-1,:]-lat_r[1:,:])*111000
        #pdb.set_trace()
            dzetady=-1.0*dzeta/dyr
        #ugeo=dzetady/f/6.378e6
            ugeo=dzetady/f
            ugeo=ugeo*9.8
        
#        pdb.set_trace()
#        uek=roms_tau/(roms_f*roms_rho)
#        roms_w=dataset['w'][0,-3,:,:]
#        roms_lat=dataset['lat_rho']
#        roms_lon=dataset['lon_rho']
            roms_temp = dataset['temp_sur']
            roms_time = dataset['ocean_time']
        #fileid.close()
#        roms_temp_latitude = roms_temp['lat_rho'].values[:,0]
#        roms_temp_longitude = roms_temp['lon_rho'].values[0,:]
#        roms_temp = roms_temp.assign_coords({"eta_rho":roms_temp_latitude, "xi_rho":roms_temp_longitude})
#        roms_temp = roms_temp.rename({"eta_rho":"latitude", "xi_rho":"longitude"})
#        roms_temp = roms_temp.drop('lat_rho', errors='ignore')
#        roms_temp = roms_temp.drop('lon_rho', errors='ignore')
#        roms_temp = roms_temp.drop('time_run', errors='ignore')
#
# Do we need to reshape the w array.  Do we need to truncate dimensions (yes)
# We want to append on which axis of the array...
#
#        roms_temp = roms_temp.transpose('ocean_time','latitude','longitude')
#        roms_temp=np.squeeze(roms_temp)
#
#        t=np.ravel(roms_temp)
#        xl=np.ravel(lon)
#        yl=np.ravel(lat)
#        zgrid=griddata((xl,yl),t,(mx,my),method='linear')
            if io==0:
            #bigtemp=np.expand_dims(uek,axis=0)
                bigtemp=np.expand_dims(we,axis=0)
                bigugeo=np.expand_dims(ugeo,axis=0)
                bigsfctemp=roms_temp
            #bigsfctemp=np.expand_dims(roms_temp,axis=0)
#            bigtemp=np.expand_dims(roms_w,axis=0)
                bigtime=otime
                io=1
            else:
                bigtime=np.append(bigtime,otime)
            #btmp=np.expand_dims(uek,axis=0)
                btmp=np.expand_dims(we,axis=0)
            #btmp=np.expand_dims(roms_w,axis=0)
                utmp=np.expand_dims(ugeo,axis=0)
            #ttmp=np.expand_dims(roms_temp,axis=0)
                bigtemp=np.vstack((bigtemp,btmp))
                bigugeo=np.vstack((bigugeo,utmp))
                bigsfctemp=np.vstack((bigsfctemp,roms_temp))
### this works for CO-OPS site
##        except Exception as e:
##            print('Exceptions '+str(e))
##            #pdb.set_trace()
##
##            urlstr=urlpre2+syear+'/'+smonth+'/'+sday+'/'+filestr+forehour+'.'+syear+smonth+sday+filepost
##            print(urlstr)
##    # ocean time is relative to 2016-01-01
##    # It turns out we can have missing nowcast files at ncei so we need to trap for that
##            try:
##                dataset=xr.open_dataset(urlstr)
##                ioerr=0
##            except HTTPError as err:
##                if (err.code==502) or (err.code==503):
##                    try:
##                        dataset=xr.open_dataset(urlstr)
##                        ioerr=0
##                    except Exception as e:
##                        print('Exception '+str(e))
##                        ioerr=1
##                else:
##                    print('Some other error occurred')
##                    ioerr=1
##                        
###
##            if ioerr==0:
##                lat=dataset['lat_rho']
##                lon=dataset['lon_rho']
##    #
##                otime=dataset['ocean_time']
##                roms_temp = dataset['temp_sur']
##                roms_time = dataset['ocean_time']
##                roms_temp_latitude = roms_temp['lat_rho'].values[:,0]
##                roms_temp_longitude = roms_temp['lon_rho'].values[0,:]
##                roms_temp = roms_temp.assign_coords({"eta_rho":roms_temp_latitude, "xi_rho":roms_temp_longitude})
##                roms_temp = roms_temp.rename({"eta_rho":"latitude", "xi_rho":"longitude"})
##                roms_temp = roms_temp.drop('lat_rho', errors='ignore')
##                roms_temp = roms_temp.drop('lon_rho', errors='ignore')
##                roms_temp = roms_temp.drop('time_run', errors='ignore')
##                roms_temp = roms_temp.transpose('ocean_time','latitude','longitude')
##                roms_temp=np.squeeze(roms_temp)
##    #
##                t=np.ravel(roms_temp)
##                xl=np.ravel(lon)
##                yl=np.ravel(lat)
##                zgrid=griddata((xl,yl),t,(mx,my),method='linear')
##                if io==0:
##                    bigtemp=np.expand_dims(zgrid,axis=0)
##                    bigtime=otime
##                    io=1
##                else:
##                    bigtime=np.append(bigtime,otime)
##                    btmp=np.expand_dims(zgrid,axis=0)
##                    bigtemp=np.vstack((bigtemp,btmp))
##        except:
##            print(urlstr+' is missing from set')
##            # what if all the model files are missing?  This should never happen....            
    # average in time
    #pdb.set_trace()
    if ioerr==0:
    #    meantemp1=np.mean(bigtemp,axis=0)
    #    meantime=pd.Series(bigtime).mean()
    # No need to keep big array and average as differnce between interpolated data and avraged big array that is
    # downsampled is in the 1e-6 range.  So in the noise of the computation.
    #meantemp2=np.mean(testtemp,axis=0)
    #tt=np.ravel(meantemp2)
    #qgrid=griddata((xl,yl),tt,(mx,my),method='linear')
    #pdb.set_trace()
    
        #return [bigtime, bigtemp,lat,lon]
        return [bigtime, bigtemp, bigugeo, bigsfctemp,lat_u,lon_u,lat_v,lon_v,lat_r,lon_r]
    else:
        return 1
