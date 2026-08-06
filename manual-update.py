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
all_floats = False # upload to all active floats if true
# only used if `all_floats` is false
user_imei_list = [
    '300125062902880', '300125062426150', '300125062423120',
    '300125062031400', '300125062035430', '300534060123910',
    '300125062907910', '300125062909910', '300125063319510',
    '300125063310200', '300125063315260', '300125063318510',
    '300125063419060', '300125063414050', '300125063413300',
    '300125063217740', '300125063211730', '300125063213730',
    '300125063215730', '300125063415280', '300125063313520',
    '300125063411300', '300125063318200', '300125063217730',
    '300125063128670', '300125063212730', '300125063712060',
] 
exclude_floats = ['300125000000000'] # exclude floats from "all", only used if `all_floats` is true

user_message = f'Update vertical resolution of CTS5 bio-optics'

#------------------------------------------------------------------------------
# connect to DFO FTP server
#------------------------------------------------------------------------------

url = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]
ftp = ftplib.FTP(url, user=username, passwd=password)
logfile = 'log/auto-update-log.log'

#------------------------------------------------------------------------------
# define floats to update
#------------------------------------------------------------------------------

active = []
ct = pd.Timestamp('now', tz='utc')
if all_floats:
    active = [imei for imei in ftp.nlst() if (ct - ppy.file_time(ftp.nlst(f'{imei}/*.bin')) < pd.Timedelta(days=12)) and (imei not in exclude_floats)]
imei_list = active if all_floats else user_imei_list

#------------------------------------------------------------------------------
# create command files and uplaod
#------------------------------------------------------------------------------

imei_dir_list = ftp.nlst()

for imei in imei_list:
    if imei not in imei_dir_list:
        continue
    print(f'Updating IMEI {imei}...')
    filename = f'commands/{ct.year}{ct.month:02d}{ct.day:02d}_{imei}_manual_time_update_cmd.txt'
    new_time = np.random.randint(24) if randomize else user_time
    with open(filename, 'w') as f:
        f.write('!param-sensor_04-14:10\r\n')
        f.write('!param-sensor_04-23:50\r\n')
        f.write('!param-sensor_04-32:50\r\n')
        f.write('!param-sensor_04-41:2\r\n')
        f.write('!param-sensor_04-49:1980\r\n')
    with open(filename, 'rb') as f:
        ftp.storbinary(f'STOR {imei}/remote/_command.txt', f)

with open(logfile, 'a') as f:
    f.write(f'\n[{ct.year:04d}-{ct.month:02d}-{ct.day:02d}] {user_message}')

ftp.quit()