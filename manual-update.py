#!/usr/env/python

import sys
import ftplib

import numpy as np
import pandas as pd

import provorpy as ppy

#------------------------------------------------------------------------------
# define method
#------------------------------------------------------------------------------

randomize = True
user_time = 8 # only used if `randomize` is false
all_floats = True # upload to all active floats if true
user_imei_list = [] # only used if `all_floats` is false
exclude_floats = ['300125061378340'] # exclude floats from "all", only used if `all_floats` is true

user_message = f'Randomize start times of all floats except {exclude_floats[0]} (already updated) to kickstart auto updates'

#------------------------------------------------------------------------------
# connect to DFO FTP server
#------------------------------------------------------------------------------

url, username = ppy.get_ftp_info()
ftp = ftplib.FTP(url, user=username, passwd=sys.argv[1])
logfile = 'log/auto-update-log.log'

#------------------------------------------------------------------------------
# define floats to update
#------------------------------------------------------------------------------

ct = pd.Timestamp('now', tz='utc')
active = [imei for imei in ftp.nlst() if (ct - ppy.file_time(ftp.nlst(f'{imei}/*.bin')) < pd.Timedelta(days=12)) and (imei not in exclude_floats)]
imei_list = active if all_floats else user_imei_list

#------------------------------------------------------------------------------
# create command files and uplaod
#------------------------------------------------------------------------------

for imei in imei_list:
    filename = f'commands/{ct.year}{ct.month}{ct.day}_{imei}_manual_time_update_cmd.txt'
    new_time = np.random.randint(24) if randomize else user_time
    with open(filename, 'w') as f:
        f.write(f'!PM 4 {new_time:d}\r\n')
    with open(filename, 'rb') as f:
        ftp.storbinary(f'STOR {imei}/RUDICS_cmd.txt', f)

with open(logfile, 'a') as f:
    f.write(f'\n[{ct.year:04d}-{ct.month:02d}-{ct.day:02d}] {user_message}')

ftp.close()