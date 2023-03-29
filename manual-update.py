#!/usr/env/python

import ftplib
from io import BytesIO

import pandas as pd
import provorpy as ppy

#------------------------------------------------------------------------------
# connect to DFO FTP server
#------------------------------------------------------------------------------

url, username, password = ppy.get_ftp_info()
ftp = ftplib.FTP(url, user=username, passwd=password)
ct = pd.Timestamp('now', tz='utc')
imei_numbers = ftp.nlst()
logfile = 'log/auto-update-log.log'