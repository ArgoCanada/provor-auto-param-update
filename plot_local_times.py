
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='ticks', palette='colorblind')

import timezonefinder
tf = timezonefinder.TimezoneFinder()
import pytz

import argopandas as argo

ix = argo.prof.subset_date('2021-01')
ix = ix.loc[ix.institution == 'ME']
ix = ix.loc[ix.profiler_type == 836] # provors
prof = ix.prof
ix['wmo'] = [prof.PLATFORM_NUMBER.loc[f,0] for f in prof.index.unique('file')]
ix['cycle'] = [prof.CYCLE_NUMBER.loc[f,0] for f in prof.index.unique('file')]

for wmo in ix['wmo'].unique():
    if not ix.cycle.loc[ix.wmo == wmo].isin([1]).any():
        ix = ix.loc[~(ix.wmo == wmo)]

ix = ix.loc[(ix.latitude.notna()) & (ix.longitude.notna())]
ix['timezone'] = [pytz.timezone(tf.certain_timezone_at(lat=lat, lng=lon)) for lat, lon in zip(ix.latitude, ix.longitude)]
ix['local_time'] = [utc_time.tz_convert(tz) for utc_time, tz in zip(ix.date, ix.timezone)]
ix['surface_hour'] = [local_time.hour + 0.5 for local_time in ix.local_time]
ix['surface_time'] = [local_time.hour + local_time.minute/60 for local_time in ix.local_time]
ix['surface_time'] = [time.hour + time.minute/60 for time in ix.date]

fig, ax = plt.subplots()
sns.lineplot(data=ix, x='date', y='surface_time', hue='wmo', style='wmo', dashes=False, markers=ix.wmo.unique().shape[0]*['s'], ax=ax)
plt.show()

for wmo in ix['wmo'].unique():
    if ix.loc[ix.wmo == wmo].surface_hour.std() < 4:
        print(
            wmo, 
            f'{ix.loc[ix.wmo == wmo].surface_hour.std():.1f}',
            ix.loc[ix.wmo == wmo].date.iloc[-1],
            ix.loc[ix.wmo == wmo].timezone.iloc[0]
        )