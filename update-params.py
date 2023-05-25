#!/usr/env/python

import sys
import ftplib
from io import BytesIO

import pandas as pd
import provorpy as ppy

update_from_command_file = True
update_from_user_list = False

#------------------------------------------------------------------------------
# connect to DFO FTP server
#------------------------------------------------------------------------------

password = sys.argv[1]
url, username = ppy.get_ftp_info()
ftp = ftplib.FTP(url, user=username, passwd=password)
ct = pd.Timestamp('now', tz='utc')
imei_numbers = ftp.nlst()
logfile = 'log/auto-update-log.log'

imei_exclude = ['300125061075760', '300125061070720']

print(imei_numbers)

imei_numbers = list(set(imei_numbers) - set(imei_exclude))

print(imei_numbers)

#------------------------------------------------------------------------------
# check timing info, previous commands
#------------------------------------------------------------------------------

update = False
for imei in imei_numbers:

    # get most recent profile time for each float
    last_profile_time = ppy.file_time(ftp.nlst(f'{imei}/*.bin'))
    print(imei, last_profile_time)
    within_last_day = ct - last_profile_time < pd.Timedelta(hours=26)
    last_command_time = ppy.file_time(ftp.nlst(f'{imei}/*cmd.txt'))
    recent_command = abs(last_command_time - last_profile_time) < pd.Timedelta(hours=12)
    param_update = within_last_day 

    if param_update:

        update = True
        print(f'Updating {imei}...')

        if update_from_command_file:
            # check time of command file - make sure it corresponds to this profile
            # effectively this means that the process must be manually started with 
            # human uploading a command file. Note sending PV=0 to tested floats could
            # cause an exception to this rule
            last_command_file = ftp.nlst(f'{imei}/*.txt')[-1]
            r = BytesIO()
            ftp.retrbinary(f'RETR {last_command_file}', r.write)
            df = ppy.read_cmd_response(r)
            new_time = df.Value.loc['PM 4'] - 5 if 'PM 4' in df.index else last_profile_time.hour - 5
            new_time = new_time + 24 if new_time < 0 else new_time
        elif update_from_user_list: # this does not work right now - need a way to do it per float?
            df = pd.read_csv(f'{imei}_time_list.csv')
            new_time = df.param.iloc[0]
            df.iloc[:-1] = df.iloc[1:]
            df.iloc[-1] = new_time
            df.to_csv('time_list.csv')
        else:
            raise ValueError('No source for new time selected')
    
        filename = f'commands/{ct.year}{ct.month}{ct.day}_{imei}_auto_time_update_cmd.txt'
        with open(filename, 'w') as f:
            f.write(f'!PM 4 {new_time:d}\r\n')
        
        with open(filename, 'rb') as f:
            ftp.storbinary(f'STOR {imei}/remote/RUDICS_cmd.txt', f)
        
        with open(logfile, 'a') as f:
            old_time = df.Value.loc['PM 4'] if 'PM 4' in df.index else last_profile_time.hour
            f.write(f'\n[{ct.year:04d}-{ct.month:02d}-{ct.day:02d}] Updated {imei} surfacing time from {old_time} to {new_time}')
    
if update:
    with open(logfile, 'a') as f:
        f.write(f'\n[{ct.year:04d}-{ct.month:02d}-{ct.day:02d}] No floats to be updated today')
