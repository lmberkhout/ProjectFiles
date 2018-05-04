from __future__ import print_function, division, absolute_import

import numpy as np
import re
import os
import glob
from astropy.time import Time
from astropy.coordinates import Angle
from astropy import units
import spec_calcs

# read in the data files
directory = './h2c/'
h2c_files = sorted(glob.glob(os.path.join(directory, 'acc_*.dat')))
n_files = len(h2c_files)

# build uvw array (separation coordinates for each baseline)
uvw_dict = {}
dates = []
n_ants = np.zeros(n_files, dtype=int)
n_baselines = np.zeros(n_files, dtype=int)
for f_ind, filename in enumerate(h2c_files):
    date_str = re.findall(r'\d+', os.path.basename(filename))[0]
    dates.append(Time('20' + date_str[0:2] + '-' + date_str[2:4] + '-' + date_str[4:6] + 'T00:00:00', scale='utc'))
    ant_names = np.loadtxt(filename, usecols=(0,), dtype=str)
    ant_nums = [int(re.findall(r'\d+', name)[0]) for name in ant_names]
    data = np.loadtxt(filename, usecols=(1, 2, 3))
    eastings = data[:, 0]
    northings = data[:, 1]
    altitudes = data[:, 1]
    n_ants[f_ind] = ant_names.shape[0]
    n_baselines[f_ind] = int(n_ants[f_ind] * (n_ants[f_ind] - 1) / 2)

    uvw_array = np.zeros((n_baselines[f_ind], 3), dtype=float)
    bl_ind = 0
    for ind1, ant1 in enumerate(ant_nums):
        for ind2, ant2 in enumerate(ant_nums):
            if ant1 < ant2:
                uvw_array[bl_ind, :] = [eastings[ind1] - eastings[ind2], northings[ind1] - northings[ind2],
                                        altitudes[ind1] - altitudes[ind2]]
                bl_ind += 1
    uvw_dict[f_ind] = uvw_array

# define max decorrelation percentages to save
max_decorr = [0.1, 0.05, 0.01]

# define angles off-zenith at which to compute decorrelations
zen_angle = [Angle(20., units.degree)]

# define correlator specs
corr_specs = []

# first spec: no FS, 2048 channels, 10s integration
c = {}
c['fs_int_time'] = 10. * units.s
c['n_channels'] = 2048
c['post_fs_int_time'] = 10. * units.s
corr_specs.append(c)

# second spec: no FS, 4096 channels, 10s integration
c = {}
c['fs_int_time'] = 10. * units.s
c['n_channels'] = 4096
c['post_fs_int_time'] = 10. * units.s
corr_specs.append(c)

# third spec: FS, 2048 channels, 10s integration
c = {}
c['fs_int_time'] = 0.1 * units.s
c['n_channels'] = 2048
c['post_fs_int_time'] = 10. * units.s
corr_specs.append(c)

# fourth spec: FS, 4096 channels, 10s integration
c = {}
c['fs_int_time'] = 0.1 * units.s
c['n_channels'] = 4096
c['post_fs_int_time'] = 10. * units.s
corr_specs.append(c)

# fifth spec: FS, 8192 channels, 2s integration
c = {}
c['fs_int_time'] = 0.1 * units.s
c['n_channels'] = 8192
c['post_fs_int_time'] = 2. * units.s
corr_specs.append(c)

# loop over different combinations
for decorr in max_decorr:
    for zang in zen_angle:
        for i, cspec in enumerate(corr_specs):
            # unpack correlator specs
            integration_time = cspec['fs_int_time']
            fringe_stop_int_time = cspec['post_fs_int_time']
            n_channels = cspec['n_channels']
            frequency = 250. * units.MHz
            chan_width = frequency / n_channels

            bda_savings = np.zeros((n_files,), dtype=float)
            for f_ind in range(n_files):
                uvw = uvw_dict[f_ind]
                for bl in range(uvw.shape[0]):
                    lx = np.abs(uvw[bl, 0]) * units.m
                    ly = np.abs(uvw[bl, 1]) * units.m
                    length = np.sqrt(lx**2 + ly**2)

                    comp_fac = spec_calcs.bda_compression_factor(max_decorr=decorr, frequency=frequency, baseline=length,
                                                                 corr_FoV=zang, n_channels=n_channels, chan_width=chan_width,
                                                                 integration_time=integration_time,
                                                                 fringe_stop_int_time=fringe_stop_int_time, decorr_rate='quadratic',
                                                                 lx=lx, ly=ly)
                    bda_savings[f_ind] += comp_fac['compression_factor']

            # add extra factor for auto-correlations; assume no compression
            bda_savings += n_ants

            # normalize by number of baselines; "n_baselines" is only number of cross-correlations
            bda_savings /= (n_baselines + n_ants)

            # build file name and save out
            out_fn = "bda_savings_decorr_{0:02d}_zang_{1:d}_cspec_{2:d}.txt".format(int(100 * decorr), int(zang.value), i)
            print("Saving {}...".format(out_fn))
            with open(out_fn, 'w') as f:
                print("# max_decorr: {:d}%".format(int(100 * decorr)), file=f)
                print("# angle off zenith: {:d} degrees".format(int(zang.value)), file=f)
                print("# fs_int_time: {:5.2f} seconds".format(integration_time), file=f)
                print("# post_fs_int_time: {:5.2f} seconds".format(fringe_stop_int_time), file=f)
                print("# n_channels: {:d}".format(n_channels), file=f)
                for f_ind in range(n_files):
                    print("{0}  {1:6.4f}".format(dates[f_ind], bda_savings[f_ind]), file=f)
