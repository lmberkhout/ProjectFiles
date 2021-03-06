import numpy as np
from astropy import constants as const
from astropy.coordinates import Angle
from astropy import units
import textwrap
default_wrap_len = 100

hera_latitude = Angle('-30:43:17.5', units.deg)
default_n_channels = 4096


def print_desc_val(description, val, wrap_len):
    print(textwrap.fill(description, width=wrap_len))
    if not isinstance(val, (list, np.ndarray)):
        print('{:.{prec}f}'.format(val, prec=2))
    else:
        print(val)


def averaging_params(max_decorr=0.1, frequency=(250. * 1e6 * units.Hz),
                     baseline=(870 * units.m), corr_FoV=Angle(90., units.degree),
                     latitude=hera_latitude, verbose=False, wrap_len=default_wrap_len):

    wavelength = const.c / frequency.to(1 / units.s)
    earth_rot_speed = (Angle(360, units.deg) / units.sday).to(units.arcminute / units.s)

    params = {}

    max_resolution = Angle(np.arcsin(wavelength / baseline), units.radian)
    params['max_resolution'] = max_resolution
    if verbose:
        print_desc_val('Max resolution:', max_resolution.to(units.arcminute), wrap_len)

    integration_time = (max_resolution * max_decorr).to(units.arcminute) / earth_rot_speed
    params['integration_time'] = integration_time
    if verbose:
        print_desc_val('Max integration time required to keep the decorrelation '
                       'due to time integrating under max_decorr on the longest '
                       'baselines:', integration_time, wrap_len)

    channel_width = ((const.c * max_decorr) / (baseline * np.sin(corr_FoV.to(units.rad)))).to(units.kHz)
    params['channel_width'] = channel_width
    if verbose:
        print_desc_val('Max channel width to keep the decorrelation due to channel '
                       'width under max_decorr for a {fov} degree correlator '
                       'FoV on the longest baselines:'.format(fov=corr_FoV.degree),
                       channel_width, wrap_len)

    # After fringe stopping, the rotation is from the sky rotating in the beam
    # This is slower, so we can sum in time to longer integrations
    # (this summing does cause more decorrelation but it's better than without
    # fringe stopping and it decreases data rates)
    fringe_stopped_int_time = ((max_resolution.to(units.arcminute) * max_decorr) /
                               (np.sin(corr_FoV.radian) * earth_rot_speed * abs(np.sin(hera_latitude))))
    params['fringe_stopped_int_time'] = fringe_stopped_int_time
    if verbose:
        print_desc_val('Max integration time to keep the decorrelation due to time '
                       'integrating after fringe stopping under max_decorr for a {fov} '
                       'degree correlator FoV on the longest baselines:'.
                       format(fov=corr_FoV.degree), fringe_stopped_int_time, wrap_len)

    return params


def decorrelations(max_decorr=0.1, frequency=(250. * 1e6 * units.Hz),
                   baseline=(870 * units.m), corr_FoV=Angle(90., units.degree),
                   n_channels=default_n_channels, chan_width=(250 * units.MHz) / default_n_channels,
                   integration_time=(.1 * units.s),
                   fringe_stop_int_time=(10 * units.s),
                   verbose=False, wrap_len=default_wrap_len, decorr_rate='linear',
                   lx=(100 * units.m), ly=(100 * units.m)):

    wavelength = const.c / frequency.to(1 / units.s)
    earth_rot_speed = (Angle(360, units.deg) / units.sday).to(units.arcminute / units.s)
    max_resolution = Angle(np.arcsin(wavelength / baseline), units.radian)

    decorrelations = {}

    decorr_int_time = integration_time * earth_rot_speed / max_resolution.to(units.arcminute)
    decorrelations['integration_time'] = decorr_int_time
    if verbose:
        print_desc_val('Decorrelation fraction due to integration time on '
                       'the longest baseline', decorr_int_time, wrap_len)

    resolution_max_decorr_int_time = integration_time * earth_rot_speed / max_decorr
    baseline_max_decorr_int_time = wavelength / np.sin(resolution_max_decorr_int_time.to(units.rad))
    decorrelations['baseline_max_decorr_int_time'] = baseline_max_decorr_int_time
    if verbose:
        print_desc_val('Longest E-W baseline with less than {decorr}% decorrelation due to '
                       'integration time '.format(decorr=max_decorr * 100),
                       baseline_max_decorr_int_time, wrap_len)

    decorr_chan_width = (chan_width.to(1 / units.s) * baseline *
                         np.sin(corr_FoV.to(units.rad)) / const.c)
    decorrelations['decorr_chan_width'] = decorr_chan_width
    if verbose:
        print_desc_val('Decorrelation due to channel width for a {fov} degree '
                       'correlator FoV for the longest baseline'.
                       format(fov=corr_FoV.degree), decorr_chan_width, wrap_len)

    baseline_max_decorr_channel_width = (max_decorr * const.c /
                                         (chan_width.to(1 / units.s) *
                                          np.sin(corr_FoV.to(units.rad))))
    decorrelations['baseline_max_decorr_channel_width'] = baseline_max_decorr_channel_width
    if verbose:
        print_desc_val('Longest baseline for a {fov} degree correlator FoV with '
                       'less than {decorr}% decorrelation due to channel width'.
                       format(fov=corr_FoV.degree, decorr=max_decorr * 100),
                       baseline_max_decorr_channel_width, wrap_len)

    sin_fov = (const.c * max_decorr) / (baseline * chan_width.to(1 / units.s))
    if isinstance(sin_fov, np.ndarray) and not sin_fov.shape == ():
        sin_fov[np.where(sin_fov > 1)[0]] = 1
    else:
        if sin_fov > 1:
            sin_fov = 1

    corr_FoV_max_decorr = Angle(np.arcsin(sin_fov), units.radian)
    decorrelations['corr_FoV_max_decorr'] = corr_FoV_max_decorr
    if verbose:
        print_desc_val('Correlator FoV with less than {decorr}% decorrelation '
                       'due to channel width for the longest baseline'.
                       format(decorr=max_decorr * 100),
                       corr_FoV_max_decorr.to(units.degree), wrap_len)

    if decorr_rate == 'linear':
        decorr_fringe_stop = ((fringe_stop_int_time * np.sin(corr_FoV.radian) *
                               earth_rot_speed * abs(np.sin(hera_latitude))) /
                              max_resolution.to(units.arcminute))
    elif decorr_rate == 'quadratic':
        decorr_fringe_stop, max_rfac = decorr_post_fs_int_time_quad(lx, ly, fringe_stop_int_time,
                                                                    corr_FoV, earth_rot_speed, wavelength)
        decorrelations['max_rfac'] = max_rfac

    decorrelations['decorr_fringe_stop'] = decorr_fringe_stop
    if verbose:
        print_desc_val('Decorrelation due to time integrating after fringe '
                       'stopping for a {fov} degree correlator FoV for the '
                       'longest baseline'.format(fov=corr_FoV.degree),
                       decorr_fringe_stop, wrap_len)

    sin_fov = (max_resolution.to(units.arcminute) * max_decorr /
               (fringe_stop_int_time * earth_rot_speed * abs(np.sin(hera_latitude))))
    if isinstance(sin_fov, np.ndarray) and not sin_fov.shape == ():
        sin_fov[np.where(sin_fov > 1)[0]] = 1
    else:
        if sin_fov > 1:
            sin_fov = 1

    corr_FoV_fringe_stop_max_decorr = Angle(np.arcsin(sin_fov), units.radian)
    decorrelations['corr_FoV_fringe_stop_max_decorr'] = corr_FoV_fringe_stop_max_decorr
    if verbose:
        print_desc_val('Correlator FoV with less than {decorr}% decorrelation '
                       'just due to time integrating after fringe stopping '
                       'for the longest baseline'.format(decorr=max_decorr * 100),
                       corr_FoV_fringe_stop_max_decorr.to(units.degree), wrap_len)
        print('')
        print('Decorrelation factors actually need to be combined!')
        print('')

    pre_fs_total_decorr = 1 - (1 - decorr_int_time) * (1 - decorr_chan_width)
    decorrelations['pre_fs_total_decorr'] = pre_fs_total_decorr
    if verbose:
        print_desc_val('Net decorrelation before fringe stopping due to integration '
                       'time and channel width for {fov} degree correlator FoV '
                       'for the longest baseline'.format(fov=corr_FoV.degree),
                       pre_fs_total_decorr, wrap_len)

    sin_fov = (((1 - (1 - max_decorr) / (1 - decorr_int_time)) * const.c) /
               (baseline * chan_width.to(1 / units.s)))
    if isinstance(sin_fov, np.ndarray) and not sin_fov.shape == ():
        sin_fov[np.where(decorr_int_time > max_decorr)[0]] = 0
        sin_fov[np.where(sin_fov > 1)[0]] = 1
    else:
        if decorr_int_time > max_decorr:
            sin_fov = 0
        if sin_fov > 1:
            sin_fov = 1
    pre_fs_corr_FoV_max_decorr = Angle(np.arcsin(sin_fov), units.radian)

    decorrelations['pre_fs_corr_FoV_max_decorr'] = pre_fs_corr_FoV_max_decorr
    if verbose:
        print_desc_val('Correlator FoV before fringe stopping with less than '
                       '{decorr}% decorrelation due to integration time and '
                       'channel width for the longest baseline'.
                       format(decorr=max_decorr * 100),
                       pre_fs_corr_FoV_max_decorr.to(units.degree), wrap_len)

    post_fs_total_decorr = 1 - (1 - pre_fs_total_decorr) * (1 - decorr_fringe_stop)
    decorrelations['post_fs_total_decorr'] = post_fs_total_decorr
    if verbose:
        print_desc_val('Total decorrelation after fringe stopping and '
                       'integrating for a {fov} degree correlator FoV'.
                       format(fov=corr_FoV.degree),
                       post_fs_total_decorr, wrap_len)

    # calculate correlator FoV after fringe stopping and integrating with
    # total decorrelation under max_decorr (10%) for the longest baseline
    # This is a quadratic in sin(FoV), so takes some setup
    # form: a_term * sin(FoV)**2 + b_term * sin(FoV) + c_term
    a_term = (baseline * chan_width.to(1 / units.s) * fringe_stop_int_time *
              earth_rot_speed * abs(np.sin(hera_latitude))) / (const.c * max_resolution.to(units.arcminute))
    b_term = (-1) * (baseline * chan_width.to(1 / units.s) / const.c +
                     fringe_stop_int_time * earth_rot_speed * abs(np.sin(hera_latitude)) /
                     (max_resolution.to(units.arcminute)))
    c_term = 1 - (1 - max_decorr) / (1 - decorr_int_time)
    sin_fov = ((-1) * b_term - np.sqrt(b_term**2 - 4 * a_term * c_term)) / (2 * a_term)

    if isinstance(sin_fov, np.ndarray) and not sin_fov.shape == ():
        sin_fov[np.where(decorr_int_time > max_decorr)[0]] = 0
        sin_fov[np.where(sin_fov > 1)[0]] = 1
    else:
        if decorr_int_time > max_decorr:
            sin_fov = 0
        if sin_fov > 1:
            sin_fov = 1
    post_fs_corr_FoV_max_decorr = Angle(np.arcsin(sin_fov), units.rad)

    decorrelations['post_fs_corr_FoV_max_decorr'] = post_fs_corr_FoV_max_decorr
    if verbose:
        print_desc_val('Correlator FoV after fringe stopping and integrating '
                       'with less than {decorr}% total decorrelation for the '
                       'longest baseline'.format(decorr=max_decorr * 100),
                       post_fs_corr_FoV_max_decorr.to(units.degree), wrap_len)

    return decorrelations


def data_rates(integration_time=(.1 * units.s), fringe_stop_int_time=(10 * units.s),
               n_antennas=350, n_channels=default_n_channels * 3 / 4,
               bytes_per_vis=(8 * units.byte)):

    sum_diff_factor = 2
    n_polarizations = 4

    Naive_data_rate = ((n_channels * (n_antennas * (n_antennas + 1) / 2) * n_polarizations *
                        bytes_per_vis * sum_diff_factor / integration_time))

    post_fringe_stop_data_rate = ((n_channels * (n_antennas * (n_antennas + 1) / 2) * n_polarizations *
                                   bytes_per_vis * sum_diff_factor / fringe_stop_int_time))

    return Naive_data_rate, post_fringe_stop_data_rate


def bda_compression_factor(max_decorr=0.1, frequency=(250. * 1e6 * units.Hz),
                           baseline=(870 * units.m), corr_FoV=Angle(90., units.degree),
                           n_channels=default_n_channels, chan_width=(250 * units.MHz) / default_n_channels,
                           integration_time=(.1 * units.s),
                           fringe_stop_int_time=(10 * units.s), decorr_rate='linear', lx=(14.6 * units.m),
                           ly = (14.6 * units.m), verbose=False, wrap_len=default_wrap_len):

    compression_factor = {}

    # calculate the total decorrelation for this given baseline and correlator settings
    decorr = decorrelations(max_decorr, frequency, baseline, corr_FoV, n_channels, chan_width,
                            integration_time, fringe_stop_int_time, verbose, wrap_len, decorr_rate=decorr_rate,
                            lx=lx, ly=ly)

    if decorr['post_fs_total_decorr'] < max_decorr:
        # if total decorr is less than max, we can average
        wavelength = const.c / frequency.to(1 / units.s)
        bl_res = Angle(np.arcsin(wavelength / baseline), units.radian)
        earth_rot_speed = (Angle(360, units.deg) / units.sday).to(units.rad / units.s)
        # compute post-fringe-stopping decorrelation allowed based on total value and pre-fringe-stopping contribution
        post_fs_decorr = 1 - (1 - max_decorr) / (1 - decorr['pre_fs_total_decorr'])
        # invert post-fringe-stopped decorrelation to find maximum possible integration time
        if decorr_rate == 'linear':
            fs_int_time = (post_fs_decorr * bl_res / np.sin(corr_FoV) / earth_rot_speed
                           / np.abs(np.sin(hera_latitude))).to(units.s).value
        else:
            fs_int_time = np.sqrt(6 * post_fs_decorr / (np.pi**2 * decorr['max_rfac']))

        # compute the number of samples that can be averaged using a power-of-two scheme
        num_ints = np.floor(np.log2(fs_int_time / fringe_stop_int_time.value))
        fac = 2**(-num_ints)
        compression_factor['num_ints'] = num_ints
        compression_factor['compression_factor'] = fac
    else:
        # no compression possible
        compression_factor['num_ints'] = 1
        compression_factor['compression_factor'] = 1

    return compression_factor

def dudt(lx, ly, ha, ers, wl):
    ha = max(min(ha, Angle(90., units.degree)), Angle(-90., units.degree))
    return (lx * np.cos(ha) - ly * np.sin(ha)) * ers / wl

def dvdt(lx, ly, ha, dec, ers, wl):
    ha = max(min(ha, Angle(90., units.degree)), Angle(-90., units.degree))
    dec = max(min(dec, Angle(90., units.degree)), Angle(-90., units.degree))
    return (lx * np.sin(dec) * np.sin(ha) + ly * np.sin(dec) * np.cos(ha)) * ers / wl

def decorr_post_fs_int_time_quad(lx, ly, int_time, corr_FoV, ers, wl):
    # case 1: +l
    du = dudt(lx, ly, corr_FoV, ers, wl)
    l = np.cos(90 * units.deg + corr_FoV)
    rfac = (du * l)**2

    # case 2: -l
    du = dudt(lx, ly, -corr_FoV, ers, wl)
    l = np.cos(90 * units.deg - corr_FoV)
    rfac = max(rfac, (du * l)**2)

    # case 3: +m
    dv = dvdt(lx, ly, 0., hera_latitude + corr_FoV, ers, wl)
    m = np.cos(90 * units.deg + corr_FoV)
    rfac = max(rfac, (dv * m)**2)

    # case 4: -m
    dv = dvdt(lx, ly, 0., hera_latitude - corr_FoV, ers, wl)
    m = np.cos(90 * units.deg - corr_FoV)
    rfac = max(rfac, (dv * m)**2)

    # make sure we have the right units
    rfac = rfac.to(units.rad**2 / units.s**2)

    # add other factors; return time and max rfac value
    return np.pi**2 * (int_time.value)**2 / 6. * rfac.value, rfac.value
