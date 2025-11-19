#!/usr/bin/env python

import os
from multiprocessing import Pool

import click

import numpy as np

import astropy.stats as astats

import losoto.h5parm
import h5py

import matplotlib as mpl
from matplotlib.backends import backend_pdf
mpl.use('Agg')

import matplotlib.pyplot as plt

from nenucal import utils, __version__
from nenucal.delayflag import make_ps

# Lazy loaded:
# - astropy.stats and  astropy.convolution in astro_convolve


mpl.rcParams['image.cmap'] = 'Spectral_r'
mpl.rcParams['image.origin'] = 'lower'
mpl.rcParams['image.interpolation'] = 'nearest'
mpl.rcParams['axes.grid'] = True

t_file = click.Path(exists=True, dir_okay=False)


class GainSol(object):

    def __init__(self, time, freqs, ant, directions, pol, amp, phase):
        self.time = time
        self.freqs = freqs
        self.ant = ant
        self.dir = directions
        self.pol = pol
        self.amp = amp
        self.phase = phase
        self.d = self.amp * np.exp(1j * self.phase)


class GainSolDask:
    def __init__(self, h5file, time, freqs, ant, directions, pol, amp, phase):
        import dask.array as da

        self._h5file = h5file  # h5py.File object
        self.time = time
        self.freqs = freqs
        self.ant = ant
        self.dir = directions
        self.pol = pol
        self.amp = amp
        self.phase = phase
        self.d = amp * da.exp(1j * phase)

    def close(self):
        if self._h5file is not None:
            self._h5file.close()
            self._h5file = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


@click.group()
@click.version_option(__version__)
def main():
    ''' DPPP gains solution utilities ...'''


def ctoap(r, i):
    c = r + 1j * i
    return abs(c), np.angle(c)


def aptoc(amp, phase):
    c = amp * np.exp(1j * phase)
    return c.real, c.imag


def get_next_odd(f):
    f = int(np.ceil(f))
    return f + 1 if f % 2 == 0 else f


def clip_and_smooth(amp, phase, x_stddev, y_stddev, sigma_clip=5):
    import astropy.stats as astats
    from astropy.convolution import Gaussian2DKernel
    from astropy.convolution import convolve

    xs = get_next_odd(np.clip(10 * x_stddev, 25, 100))
    ys = get_next_odd(np.clip(10 * y_stddev, 25, 100))

    kernel = Gaussian2DKernel(x_stddev=x_stddev, y_stddev=y_stddev, x_size=xs, y_size=ys)
    c_phase = np.exp(1j * phase)

    amp = astats.sigma_clip(amp, sigma=sigma_clip, maxiters=10)
    c_phase.mask = amp.mask

    amp = convolve(amp, kernel, boundary='extend')
    p_real = convolve(c_phase.real, kernel, boundary='extend')
    p_imag = convolve(c_phase.imag, kernel, boundary='extend')

    return amp, np.angle(p_real + 1j * p_imag)


def smooth_sol(sol, fwhm_time, main_fwhm_time, fwhm_freq, main_fwhm_freq, main_name='main', sigma_clip=5):
    dx_min = (sol.time[1] - sol.time[0]) / 60.
    dx_mhz = (sol.freqs[1] - sol.freqs[0]) * 1e-6

    s_amp = np.zeros_like(sol.amp)
    s_phase = np.zeros_like(sol.phase)

    for i_c in range(len(sol.dir)):
        if sol.dir[i_c].strip('[] ').lower() == main_name:
            c_fwhm_time = main_fwhm_time
            c_fwhm_freq = main_fwhm_freq
        else:
            c_fwhm_time = fwhm_time
            c_fwhm_freq = fwhm_freq
        stddev_time = c_fwhm_time / dx_min / 2.3
        stddev_freqs = c_fwhm_freq / dx_mhz / 2.3
        print(f'Smoothing {sol.dir[i_c]} with a Gaussian kernel of FWHM {c_fwhm_time} min and {c_fwhm_freq} MHz')

        for i_s in range(len(sol.ant)):
            for i_p in range(len(sol.pol)):
                a, p = clip_and_smooth(sol.amp[:, :, i_s, i_c, i_p], sol.phase[:, :, i_s, i_c, i_p], 
                                      stddev_freqs, stddev_time, sigma_clip=sigma_clip)
                s_amp[:, :, i_s, i_c, i_p] = a
                s_phase[:, :, i_s, i_c, i_p] = p

    return GainSol(sol.time, sol.freqs, sol.ant, sol.dir, sol.amp, s_amp, s_phase)


def open_sol(file_h5):
    # amp: time, freqs, antm, dir, pol
    sol_file = None
    try:
        sol_file = losoto.h5parm.h5parm(file_h5)
        solset = sol_file.getSolsets()[0]
        soltab, soltab_phase = solset.getSoltabs(useCache=True)

        ant = soltab.getAxisValues('ant')
        directions = soltab.getAxisValues('dir')
        time = soltab.getAxisValues('time')
        pol = soltab.getAxisValues('pol')

        freqs = soltab.getAxisValues('freq')

        weight = soltab.getValues(weight=True)[0].astype(bool)
        amp = np.ma.array(soltab.getValues(weight=False)[0], mask=~weight)
        phase = np.ma.array(soltab_phase.getValues(weight=False)[0], mask=~weight)

        if directions is None:
            amp = amp[:, :, :, None, :]
            phase = phase[:, :, :, None, :]
            directions = ['di']
    finally:
        if sol_file is not None:
            sol_file.close()

    return GainSol(time, freqs, ant, directions, pol, amp, phase)


def open_sol_dask(file_h5, chunk_shape=(155, 62, 1, 1, 2)):
    import dask.array as da

    h5f = h5py.File(file_h5, 'r')  # Keep file open

    time = h5f['/sol000/amplitude000/time'][:]
    freqs = h5f['/sol000/amplitude000/freq'][:]
    ant = np.array([x.decode() if isinstance(x, bytes) else x for x in h5f['/sol000/amplitude000/ant'][:]])
    directions = np.array([x.decode() if isinstance(x, bytes) else x for x in h5f['/sol000/amplitude000/dir'][:]])
    pol = np.array([x.decode() if isinstance(x, bytes) else x for x in h5f['/sol000/amplitude000/pol'][:]])

    amp = da.from_array(h5f['/sol000/amplitude000/val'], chunks=chunk_shape)
    phase = da.from_array(h5f['/sol000/phase000/val'], chunks=chunk_shape)
    weight = da.from_array(h5f['/sol000/amplitude000/weight'], chunks=chunk_shape).astype(bool)

    amp = da.ma.masked_where(~weight, amp)
    phase = da.ma.masked_where(~weight, phase)

    return GainSolDask(h5f, time, freqs, ant, directions, pol, amp, phase)


def get_mean_gain(gain_sols):
    ants = sorted(set([a for gain_sol in gain_sols for a in gain_sol.ant]))
    gain_sols_m = np.zeros((1, len(gain_sols[0].freqs), len(ants), 1, 2), dtype=complex)
    for i, ant in enumerate(ants):
        ant_gain_sols = []
        for gain_sol in gain_sols:
            if ant in gain_sol.ant:
                d = gain_sol.d[:, :, gain_sol.ant == ant, 0]
                d = astats.sigma_clip(d.real, maxiters=10, sigma=5) + 1j * astats.sigma_clip(d.imag, maxiters=10, sigma=5)
                time_mask = astats.sigma_clip(d.std(axis=(1, 2, 3)), sigma=2).mask
                time_mask2 = astats.sigma_clip(d.mask.sum(axis=(1, 2, 3)), sigma=2).mask
                ant_gain_sols.append(d[~(time_mask | time_mask2), :, 0])

        gain_sols_m[0, :, i, 0] = np.mean(np.concatenate(ant_gain_sols), axis=0)

    return gain_sols_m


def save_sol(file_h5, sol):
    sol_file = None
    try:
        print('Saving solutions ...')
        sol_file = losoto.h5parm.h5parm(file_h5, readonly=False)
        solset = sol_file.getSolsets()[0]
        soltab, soltab_phase = solset.getSoltabs()
        
        soltab.setValues(sol.amp)
        soltab_phase.setValues(sol.phase)
    finally:
        if sol_file is not None:
            sol_file.close()
        print('Done')


def save_new_sol(h5_file, time, freq, amps, phases, ant, direction='Main', pol=[]):
    import losoto.h5parm
    weights = np.ones_like(amps)
    
    print(ant)

    axis_vals = [time, freq, ant, ['[%s]' % direction], np.array(['XX', 'YY'])]
    axes_name = ['time', 'freq', 'ant', 'dir', 'pol']

    if os.path.exists(h5_file):
        os.remove(h5_file)
        
    print(time.shape, freq.shape, ant.shape, amps.shape, phases.shape)

    los_h5 = losoto.h5parm.h5parm(h5_file, readonly=False)
    try:
        los_h5.makeSolset('sol000')
        sol_set = los_h5.getSolset('sol000')
        sol_set.makeSoltab('amplitude', 'amplitude000', axesNames=axes_name, axesVals=axis_vals,
                           vals=amps, weights=weights)
        sol_set.makeSoltab('phase', 'phase000', axesNames=axes_name, axesVals=axis_vals, vals=phases, 
                           weights=weights)
    finally:
        los_h5.close()


def plot_sol(sol, dir, pol, data_type, filename):
    if data_type == 'Amplitude':
        v = sol.amp[:, :, :, dir, pol]
    elif data_type == 'Phase':
        v = sol.phase[:, :, :, dir, pol]
    else:
        print(f'Error: data type {data_type} unknown')
        return

    vmax = np.nanquantile(v[~v.mask & ~np.isnan(v) & (v != 0)], 0.999)
    vmin = np.nanquantile(v[~v.mask & ~np.isnan(v) & (v != 0)], 0.001)
    extent = [0, len(sol.time), sol.freqs.min() * 1e-6, sol.freqs.max() * 1e-6]

    n = v.shape[2]
    ncols, nrows = int(np.ceil(np.sqrt(n))), int(np.ceil(n / np.ceil(np.sqrt(n))))

    fig, axs = plt.subplots(ncols=ncols, nrows=nrows, sharey=True, figsize=(1 + 2 * ncols, 1 + 1.5 * nrows),
                            sharex=True)

    im = None

    for i, ax in zip(range(v.shape[2]), axs.flatten()):
        if v.shape[0] > 1 and v.shape[1] > 1:
            im = ax.imshow(v[:, :, i].T, aspect='auto', vmax=vmax, vmin=vmin, extent=extent)
        elif v.shape[0] == 1:
            ax.plot(sol.freqs * 1e-6, v[0, :, i].T)
        elif v.shape[1] == 1:
            ax.plot(v[:, 0, i].T)
        ax.text(0.025, 0.975, sol.ant[i], transform=ax.transAxes, fontsize=11, va='top')

    ylabel = ''
    xlabel = ''

    if v.shape[0] > 1 and v.shape[1] > 1 and im is not None:
        cax = fig.add_axes([0.6, 1.04, 0.39, 0.02])
        cax.set_xlabel(data_type)
        fig.colorbar(im, cax=cax, orientation='horizontal')
        xlabel = 'Time index'
        ylabel = 'Frequency [Mhz]'
    elif v.shape[0] == 1:
        xlabel = 'Frequency [MHz]'
        ylabel = data_type
    elif v.shape[1] == 1:
        xlabel = 'Time index'
        ylabel = data_type

    for ax in axs[:, 0]:
        ax.set_ylabel(ylabel)
    for ax in axs[-1, :]:
        ax.set_xlabel(xlabel)

    fig.tight_layout(pad=0)
    fig.savefig(filename, dpi=120, bbox_inches="tight")


def plot_sol_avg(freqs, gain_sols_m, ants, output_pdf, nrows=5):
    pdf = backend_pdf.PdfPages(output_pdf)

    for i in np.arange(np.ceil(gain_sols_m.shape[2] / nrows)):
        fig, axs = plt.subplots(figsize=(10, 15), nrows=nrows, sharex=True)
        for j, ax in enumerate(axs):
            k = int(i * nrows + j)
            if k >= gain_sols_m.shape[2]:
                continue
            ax.plot(freqs * 1e-6, np.abs(gain_sols_m[0, :, k, 0, :]))
            ax.text(0.05, 0.95, ants[k], transform=ax.transAxes, va='top', ha='left')
        axs[-1].set_xlabel('Frequency [MHz]')
        fig.tight_layout(pad=0)
        pdf.savefig(fig)
    pdf.close()


def plot_sol_avg_delay(freqs, gain_sols_m, ants, output_pdf, fmax=71e6, ncols=5, delay_max=7):
    nrows = int(np.ceil(gain_sols_m.shape[2] / 5))
    fig, axs = plt.subplots(figsize=(10, nrows * 2.25), ncols=ncols, nrows=nrows, sharex=True, sharey=True)
    axs = axs.flatten()
    idx = (freqs < fmax)
    gain_sols_m[np.isnan(gain_sols_m)] = 0
    for i, (ant, ax) in enumerate(zip(ants, axs)):
        delay = utils.get_delay(freqs[idx]) * 1e6
        ps = make_ps(gain_sols_m[0, idx, i, 0, :], freqs[idx])
        ps = ps / ps.max()
        ax.plot(delay, ps)
        ax.set_xlim(0, delay_max)
        ax.set_yscale('log')
        ax.text(0.05, 0.95, ant, transform=ax.transAxes, va='top', ha='left')
    fig.tight_layout(pad=0)
    fig.savefig(output_pdf)


@main.command('smooth')
@click.argument('sols', nargs=-1, type=t_file)
@click.option('--fwhm_time', help='Time coherence scale (min)', type=float, default=16)
@click.option('--fwhm_freq', help='Freq coherence scale (MHz)', type=float, default=2)
@click.option('--main_fwhm_time', help='Time coherence scale (min) for Main direction', type=float, default=20)
@click.option('--main_fwhm_freq', help='Freq coherence scale (MHz) for Main direction', type=float, default=4)
@click.option('--clip_nsigma', help='Clip solution above NSIGMA', type=float, default=4)
@click.option('--main_name', help='Name of the main direction', type=str, default='main')
def smooth(sols, fwhm_time, fwhm_freq, main_fwhm_time, main_fwhm_freq, clip_nsigma, main_name):
    ''' Smooth solutions with a Gaussian kernel'''
    for sol_file in sols:
        sol = open_sol(sol_file)
        s_sol = smooth_sol(sol, fwhm_time, main_fwhm_time, fwhm_freq, main_fwhm_freq, main_name=main_name, sigma_clip=clip_nsigma)
        save_sol(sol_file, s_sol)


@main.command('plot')
@click.argument('sols', nargs=-1, type=t_file)
@click.option('--plot_dir', help='Plot directory', type=str, default='sol_plots')
@click.option('--n_cpu', help='Number of CPU to use', type=int, default=4)
def plot(sols, plot_dir, n_cpu):
    ''' Plot solutions of the h5 files SOLS '''
    for sol_file in sols:
        sol = open_sol(sol_file)

        with Pool(n_cpu) as pool:
            for data_type in ['Amplitude', 'Phase']:
                for dir in range(len(sol.dir)):
                    for pol in range(len(sol.pol)):
                        filename = f'{data_type}_dir{sol.dir[dir]}_pol{sol.pol[pol]}.png'
                        path = os.path.join(os.path.dirname(sol_file), plot_dir, filename)

                        if not os.path.exists(os.path.dirname(path)):
                            os.makedirs(os.path.dirname(path))

                        # plot_sol(sol, dir, pol, data_type, path)
                        pool.apply_async(plot_sol, [sol, dir, pol, data_type, path])
            pool.close()
            pool.join()


# @main.command('average')
# @click.argument('obs_ids', type=str)
# @click.argument('output_h5', type=str)
# @click.option('--config', '-c', help='Data handler configuration file', type=str,
#               default='data_handler.toml', show_default=True)
# @click.option('--input_h5_name', '-i', help='Name of the input h5 file', type=str,
#               default='instrument_di_bp.h5', show_default=True)
# @click.option('--data_level', '-l', help='Level of the data', type=str, default='L2_12C40S', show_default=True)
def average(obs_ids, output_h5, config, input_h5_name, data_level):
    dh = datahandler.DataHandler.from_file(config)

    all_gain_sols_m = []
    all_freqs = []
    obs_ids = dh.get_obs_ids(obs_ids)

    for sw in dh.get_spectral_windows():
        h5_files = [f'{k}/{input_h5_name}' for k in dh.get_all_ms_path(obs_ids, [data_level], [sw])]
        gain_sols = [open_sol(h5_file) for h5_file in h5_files]
        sw_gain_sols_m = get_mean_gain(gain_sols)
        all_gain_sols_m.append(sw_gain_sols_m)
        all_freqs.append(gain_sols[0].freqs)

    gain_sols_m = np.concatenate(all_gain_sols_m, axis=1)
    freqs = np.concatenate(all_freqs)
    ants = sorted(set([a for gain_sol in gain_sols for a in gain_sol.ant]))

    plot(freqs, gain_sols_m, ants, output_h5.replace('.h5', '') + '.pdf')
    plot_delay(freqs, gain_sols_m, ants, output_h5.replace('.h5', '') + '_delay.pdf')

    save_h5(output_h5, gain_sols[0].time[:1], freqs, np.abs(gain_sols_m), 
            np.angle(gain_sols_m), np.array(ants))


if __name__ == '__main__':
    main()
