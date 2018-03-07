"""
Based on https://github.com/mommermi/callhorizons (MIT license)

Allow to read data from the JPL horizon website and from a local file
"""

import urllib.request as urllib
import numpy as np
import json
import time
import sys


class Horizon:

	# NASA horizon planets id
    Earth=399
    Sun=10
    Mercury = 199
    Venus= 299
    Mars = 499
    Jupiter = 599
    Saturn=699
    Uranus=799
    Neptune=899
    Pluto=999
    Moon=301    
    
    def __init__(self):
        self.data = None
	
    def get_mass(self, id):
		# Masses are read from the file SimplePlanetSheet.json
        mass = -1.
        with open('SimplePlanetSheet.json','r') as mfile:
            planet_sheet = json.load(mfile)
            mass = float(planet_sheet[str(id)]['Mass'])			
        return mass
		
    def call_horizon(self, id='399', start_time='1980-05-25', stop_time='1980-05-26', step_size ='1d'):
        url = "http://ssd.jpl.nasa.gov/horizons_batch.cgi?batch=l"
        url += "&TABLE_TYPE='VECTORS'" 
        url += "&CSV_FORMAT='YES'" 
        url += "&ANG_FORMAT='DEG'" 
        url += "&CAL_FORMAT='BOTH'"    
        url += "&CENTER='"+str('500@0')+"'" 
        url += "&START_TIME='"+str(start_time)+"'" 
        url += "&STOP_TIME='"+str(stop_time)+"'" 
        url += "&STEP_SIZE='"+str(step_size)+"'" 
        url += "&OUT_UNITS='"+str('AU-D')+"'" 
        url += "&REF_SYSTEM='"+str('J2000')+"'" 
        url += "&VECT_CORR='"+str('NONE')+"'"
        url += "&VEC_LABELS='"+str('YES')+"'"
        url +=  "&VEC_DELTA_T='"+str('NO')+"'"
        url += "&OBJ_DATA='"+str('NO')+"'"
        url +=  "&VEC_TABLE='"+str('3')+"'"
        url +=  "&COMMAND='"+str(id)+"'"         
		
        #sys.stdout.write("%s   \r" % (url) )
        #sys.stdout.flush()
        i = 0  # count number of connection tries
        while True:
            try:
                src = urllib.urlopen(url).readlines()
                break
            except urllib.URLError:
                time.sleep(0.1)
                # in case the HORIZONS website is blocked (due to another query)
                # wait 0.1 second and try again
            i += 1
            if i > 50:
                return 0 # website could not be reached
        in_datablock = False
        datablock = []
        for idx,line in enumerate(src):
            line = line.decode('UTF-8')
            if 'JDTDB,' in line:
                headerline = line.split(',')
            if "$$EOE\n" in line:
                in_datablock = False
            if in_datablock:
                datablock.append(line)
            if "$$SOE\n" in line:            
                in_datablock = True

        elements = []
        for line in datablock:
            line = line.split(',')

            this_el   = []
            fieldnames = []
            datatypes   = []
            # create a dictionary for each date (each line)
            for idx,item in enumerate(headerline):
           
                if (item.find('JDTDB') > -1):
                    this_el.append(np.float64(line[idx]))
                    fieldnames.append('datetime_jd')
                    datatypes.append(np.float64)
                if (item.find('Calendar Date (TDB)') > -1):
                    this_el.append(str(line[idx]))
                    fieldnames.append('cal')
                    datatypes.append(np.str)    
                if (item.find(' X') > -1):
                    this_el.append(np.float64(line[idx]))
                    fieldnames.append('x')
                    datatypes.append(np.float64) 
                if (item.find(' Y') > -1):
                    this_el.append(np.float64(line[idx]))
                    fieldnames.append('y')
                    datatypes.append(np.float64) 
                if (item.find(' Z') > -1):
                    this_el.append(np.float64(line[idx]))
                    fieldnames.append('z')
                    datatypes.append(np.float64) 
                if (item.find(' VX') > -1):
                    this_el.append(np.float64(line[idx]))
                    fieldnames.append('vx')
                    datatypes.append(np.float64) 
                if (item.find(' VY') > -1):
                    this_el.append(np.float64(line[idx]))
                    fieldnames.append('vy')
                    datatypes.append(np.float64) 
                if (item.find(' VZ') > -1):
                    this_el.append(np.float64(line[idx]))
                    fieldnames.append('vz')
                    datatypes.append(np.float64) 
                if (item.find(' LT') > -1):
                    this_el.append(np.float64(line[idx]))
                    fieldnames.append('lt')
                    datatypes.append(np.float64) 
                if (item.find(' RG') > -1):
                    this_el.append(np.float64(line[idx]))
                    fieldnames.append('rg')
                    datatypes.append(np.float64) 
                if (item.find(' RR') > -1):
                    this_el.append(np.float64(line[idx]))
                    fieldnames.append('rr')
                    datatypes.append(np.float64) 
            # combine elements with column names and data types into ndarray
                        # append targetname
     
            if len(this_el) > 0:
                elements.append(tuple(this_el))

        assert len(elements[0]) == len(fieldnames) == len(datatypes)
        self.data = np.array(elements,
                    dtype=[(str(fieldnames[i]), datatypes[i]) for i in range(len(fieldnames))])