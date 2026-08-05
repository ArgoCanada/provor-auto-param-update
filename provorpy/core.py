
from warnings import warn
import os
import copy
import pandas as pd

from . import configure

def get_ftp_info():
    config = configure.read_config()
    cfg_copy = copy.deepcopy(config)

    for k in ['ftp_url', 'ftp_username']:
        if k not in config.keys():
            ks = k.replace('ftp_', '')
            warn(f'FTP {ks} not in .config file, returning blank string. Add it by running provorpy.configure.configure({k}=...')
            cfg_copy[k] = ''

    url = cfg_copy['ftp_url']
    user = cfg_copy['ftp_username']

    return url, user

def read_tech_file_time(file):
    f = open(file, 'r') if not hasattr(file, 'read') else file
    f.seek(0)

    section = ''
    for line in f:
        line = line.decode() if type(line) is bytes else line
        if line[0] == '[':
            section = line.strip()
        if section == '[GPS]':
            if line.split('=')[0] == 'UTC':
                datestr = line.split('=')[1].split(' ')
                datestr = '20' + datestr[0] + ' ' + datestr[1]
                print(datestr)
                return pd.Timestamp(datestr, tz='utc')
        print(line)

def file_time(file, kind='cts4'):

    if hasattr(file, '__iter__') and len(file) == 0:
        return pd.Timestamp('1950-01-01', tz='utc')
    f = file[-1] if hasattr(file, '__iter__') else file
    f = file[-2] if f.split('_')[0] == 'RUDICS_cmd.txt' else f

    if kind == 'cts4':
        date_string = f.split('/')[-1].split('_')[0]
        time_string = f.split('/')[-1].split('_')[1]
    elif kind == 'cts5':
        date_string = f.split('/')[-1].split('_')[2]
        time_string = f.split('/')[-1].split('_')[3].split('.')[0]
    else:
        raise ValueError('Unrecognized input for `kind`')

    return pd.Timestamp(
        year=int(f'20{date_string[:2]}'), 
        month=int(date_string[2:4]), 
        day=int(date_string[4:]),
        hour=int(time_string[:2]), 
        minute=int(time_string[2:4]), 
        second=int(time_string[4:]), tz='utc')

def read_cmd_response(file):

    params = []
    vals = []

    f = open(file, 'r') if not hasattr(file, 'read') else file
    f.seek(0)

    for line in f:
        line = line.decode() if type(line) is bytes else line
        line = line.split('-')[0].strip()
        if line[0] == '!':
            l = line[1:]
            params.append(' '.join(l.split(' ')[:-1]))
            vals.append(int(l.split(' ')[-1]))
    
    df = pd.DataFrame(data=dict(Value=vals), index=params)

    return df