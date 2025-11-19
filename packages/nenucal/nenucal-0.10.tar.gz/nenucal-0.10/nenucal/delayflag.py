import os
import toml

import numpy as np

import scipy.signal
import scipy.ndimage
import scipy.stats

import astropy.constants as const
import astropy.stats as astats
import astropy.time as at

from . import utils, msutils
from libpipe import attrmap

import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt


TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')


def flag_time(ms_cube, threshold=0.15):
    s = ms_cube.data.shape
    mask_freqs = (ms_cube.data.mask.sum(axis=(0, 3)) > threshold * (s[0] * s[3]))[None, :, :, None]
    ms_cube.data.mask = (ms_cube.data.mask + mask_freqs).astype(bool)
    ms_cube.data_dt.mask = (ms_cube.data_dt.mask + mask_freqs[:, ::2][:, :ms_cube.data_dt.mask.shape[1]]).astype(bool)


def hpass_flag(data, fill=0, n_chan=20):
    d = data.filled(fill)
    k = scipy.signal.gaussian(10 * n_chan, n_chan)
    fit_r = scipy.ndimage.filters.convolve1d(d.real, k / k.sum(), mode='nearest', axis=0)
    fit_i = scipy.ndimage.filters.convolve1d(d.imag, k / k.sum(), mode='nearest', axis=0)
    fit = (fit_r + 1j * fit_i)
    return np.ma.array(d - fit, mask=data.mask)


def get_lst(obs_mjd, longitude=6.57):
    return at.Time(obs_mjd, scale='utc', format='mjd').sidereal_time('mean', longitude=longitude).value


def binned_sigma_clip(ru, d, bins=[0, 250], detrend_deg=0, **kargs):
    y = d.flatten()
    if detrend_deg > 0:
        detrend_y = astats.sigma_clip(y, sigma=6)
        d_fit = np.poly1d(np.polyfit(ru[~detrend_y.mask], y[~detrend_y.mask], detrend_deg))(ru)
        y = y - d_fit

    r = np.ma.zeros(y.shape)
    indices = np.digitize(ru, bins)
    for i in np.unique(indices):
        r[indices == i] = astats.sigma_clip(y[indices == i], **kargs)
    return np.ma.array(d, mask=r.mask.reshape(*d.shape))


def make_ps(d, freq, half=True, window_fct='blackmanharris'):
    s = d.shape
    w = scipy.signal.get_window(window_fct, s[0])[:, None]
    w = w / w.mean()

    if len(s) > 2:
        d = d.reshape((s[0], s[1] * s[2]))

    _, tf = utils.nudft(freq, utils.rmean(d), s[0], w=w)

    if len(s) > 2:
        tf = tf.reshape((s[0], s[1], s[2]))

    ps = abs(tf) ** 2

    if half:
        M = ps.shape[0]
        if utils.is_odd(M):
            ps = 0.5 * (ps[M // 2 + 1:] + ps[:M // 2][::-1])
        else:
            ps = 0.5 * (ps[M // 2 + 1:] + ps[1:M // 2][::-1])

    return np.ma.array(ps, mask=ps == 0)


def make_tf(d, freq, window_fct='boxcar'):
    s = d.shape
    w = scipy.signal.get_window(window_fct, s[0])[:, None]
    w = w / w.mean()

    if len(s) > 2:
        d = d.reshape((s[0], s[1] * s[2]))

    _, tf = utils.nudft(freq, utils.rmean(d), s[0], w=w)

    if len(s) > 2:
        tf = tf.reshape((s[0], s[1], s[2]))

    return tf


class DelayFlaggerResult(object):

    def __init__(self, n_times, n_sigma_i, n_sigma_v, all_m_i_masked, all_m_v_masked):
        self.n_times = n_times
        self.n_sigma_i = n_sigma_i
        self.n_sigma_v = n_sigma_v
        self.all_m_i_masked = all_m_i_masked
        self.all_m_v_masked = all_m_v_masked


class DelayFlagger(object):

    def __init__(self, ms_file, ntime_avg, data_col='DATA', umin=50, umax=400, flag_time_ratio=0.25):
        self.ms_file = ms_file
        self.ms_cube = msutils.MsDataCube.load(ms_file, umin, umax, data_col, n_time_avg=1)

        flag_time(self.ms_cube, threshold=flag_time_ratio)
        m_vis_i, m_vis_v, m_vis_dt = self._get_stokes(ntime_avg)

        half = False
        window_fct = 'blackmanharris'

        self.all_ps_dt = make_ps(m_vis_dt.filled(0), self.ms_cube.freq, half=half, window_fct=window_fct)
        self.all_ps_v = make_ps(m_vis_v.filled(0), self.ms_cube.freq, half=half, window_fct=window_fct)
        self.all_ps_i = make_ps(hpass_flag(m_vis_i).filled(0), self.ms_cube.freq, half=half, window_fct=window_fct)

        self.delay = utils.get_delay(self.ms_cube.freq * 1e-6, half=half)

        freq = self.ms_cube.freq.mean()
        self.lamb = const.c.value / freq
        self.horizon = utils.get_wedge_delay(np.radians(90), self.ms_cube.bu / self.lamb, freq) * 1e6

    def _get_stokes(self, ntime_avg=50):
        m_vis_dt = self.ms_cube.data_dt[:, :, :, 0]
        m_vis_v = 0.5 * (-1j * (self.ms_cube.data[:, :, :, 1] - self.ms_cube.data[:, :, :, 2]))
        m_vis_i = 0.5 * (self.ms_cube.data[:, :, :, 0] + self.ms_cube.data[:, :, :, 3])

        m_vis_i, m_vis_i_n = msutils.mean_consecutive(m_vis_i, axis=1, n=ntime_avg, return_n=True)
        m_vis_i = m_vis_i * np.sqrt(m_vis_i_n)

        m_vis_v, m_vis_v_n = msutils.mean_consecutive(m_vis_v, axis=1, n=ntime_avg, return_n=True)
        m_vis_v = m_vis_v * np.sqrt(m_vis_v_n)

        m_vis_dt, m_vis_dt_n = msutils.mean_consecutive(m_vis_dt, axis=1, n=ntime_avg, return_n=True)
        m_vis_dt = m_vis_dt * np.sqrt(m_vis_dt_n)

        return m_vis_i, m_vis_v, m_vis_dt

    def do_flag(self, n_times, n_sigma_i, n_sigma_v):
        all_m_i_masked = self.filter_delay_ps(self.all_ps_i, n_times, n_sigma_i)
        all_m_v_masked = self.filter_delay_ps(self.all_ps_v, n_times, n_sigma_v)

        all_m_i_masked_1 = self.filter_delay_ps(self.all_ps_i, 1, n_sigma_i)
        all_m_v_masked_1 = self.filter_delay_ps(self.all_ps_v, 1, n_sigma_v)

        all_m_i_masked.mask = all_m_i_masked.mask + all_m_i_masked_1.mask
        all_m_v_masked.mask = all_m_v_masked.mask + all_m_v_masked_1.mask

        return DelayFlaggerResult(n_times, n_sigma_i, n_sigma_v, all_m_i_masked, all_m_v_masked)

    def save_flag(self, result):
        new_mask = self.ms_cube.data.mask.copy()
        print('Before:', new_mask.sum() / self.ms_cube.data.mask.size)

        all_m_mask = result.all_m_i_masked.mask + result.all_m_v_masked.mask
        idx = list(np.linspace(0, all_m_mask.shape[1] - 1, len(self.ms_cube.time)).astype(int))
        new_mask = (new_mask + all_m_mask[:, idx].T[None, :, :, None]).astype(bool)
        print('After flagging:', new_mask.sum() / self.ms_cube.data.mask.size)

        self.ms_cube.save_flag(self.ms_file, new_mask)

    def get_delay_power_ratio_map(self, all_ps, n_times):
        all_m = []
        for i in np.arange(len(self.ms_cube.ru)):
            mean = np.mean(self.all_ps_dt[:, :, i] / 4.)
            m = np.mean(all_ps[(abs(self.delay) > 1.2 * self.horizon[i]) & (abs(self.delay) < 4), :, i], axis=0) / mean
            if np.alltrue(m.mask):
                all_m.append(np.ones((n_times)) * np.nan)
                continue
            m[m.mask] = np.nanmean(m)
            if n_times is None:
                all_m.append(m)
            else:
                all_m.append(scipy.stats.binned_statistic(np.arange(len(m)), m.filled(0),
                                                          statistic=np.ma.mean, bins=n_times)[0])

        return np.array(all_m)

    def filter_delay_ps(self, all_ps, n_times, n_sigma):
        all_m = self.get_delay_power_ratio_map(all_ps, n_times)
        ru = np.repeat(self.ms_cube.ru, n_times)

        return binned_sigma_clip(ru, all_m, sigma=n_sigma, stdfunc=astats.mad_std)

    def plot_delay_flag(self, result, plot_dir):
        cmap = mpl.cm.get_cmap('magma')
        cmap.set_bad(color='blue')
        props = dict(boxstyle='round', facecolor='white', alpha=0.8)
        extent = [0, len(self.ms_cube.ru) - 1, 0, len(self.ms_cube.time) - 1]
        lsts = get_lst(self.ms_cube.time[:] / 3600. / 24.)

        fig, (axi1, axi2, axv1, axv2) = plt.subplots(nrows=4, figsize=(12, 11), sharex=True)

        for ax1, ax2, all_m_masked, stokes in [(axi1, axi2, result.all_m_i_masked, 'I'),
                                               (axv1, axv2, result.all_m_v_masked, 'V')]:
            im = ax1.imshow(all_m_masked.data[np.argsort(self.ms_cube.ru)].T,
                            aspect='auto', vmax=2, vmin=0.9, cmap=cmap, extent=extent)
            plt.colorbar(im, ax=ax1)
            ax1.set_ylabel('LST Time (hour)')
            ax1.set_yticks(np.linspace(0, len(self.ms_cube.time) - 1, result.n_times))
            ax1.set_yticklabels(['%.1f' % lsts[int(i)] for i in ax1.get_yticks()])

            txt = f'Stokes {stokes}: Max: {np.nanmax(all_m_masked.data):.1f}, \
            Med: {np.nanmedian(all_m_masked.data):.2f}'

            ax1.text(0.05, 0.95, txt, transform=ax1.transAxes, va='top', ha='left', bbox=props)

            ax2.imshow(all_m_masked[np.argsort(self.ms_cube.ru)].T, aspect='auto',
                       vmax=2, vmin=0.9, cmap=cmap, extent=extent)
            plt.colorbar(im, ax=ax2)
            ax2.set_ylabel('LST Time (hour)')
            ax2.set_xlabel('Baseline number')
            ax2.set_yticks(np.linspace(0, len(self.ms_cube.time) - 1, result.n_times))
            ax2.set_yticklabels(['%.1f' % lsts[int(i)] for i in ax2.get_yticks()])

            txt = f'Stokes {stokes}: Max: {all_m_masked.max():.1f}, Med: \
            {np.ma.median(all_m_masked):.2f}, Flagged: {all_m_masked.mask.sum() / all_m_masked.size * 100:.1f} %'

            ax2.text(0.05, 0.95, txt, transform=ax2.transAxes, va='top', ha='left', bbox=props)

            for ax in [ax1, ax2]:
                for l in [50, 100, 150]:
                    x = np.where(self.ms_cube.ru[np.argsort(self.ms_cube.ru)] / self.lamb > l)[0]
                    if len(x) > 0:
                        ax.axvline(x[0], c='red', ls='--')
                        ax.text(x[0], 0, str(l), c='red')

        fig.tight_layout()

        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)

        fig.savefig(plot_dir + f'/all_delay_ps_mask_i{result.n_sigma_i}_v{result.n_sigma_v}.pdf')

    def plot_delay_ps_iv(self, plot_dir):
        # stat_names = self.ms_cube.ant_name
        stat_names = np.array(['STA' + str(k) for k in np.arange(56)])
        nrows = int(np.ceil(self.all_ps_i.shape[2] / 5.))
        fig, axs = plt.subplots(ncols=5, nrows=nrows, sharex=True, sharey=True, figsize=(12, 1 + nrows * 2))

        all_noise_levels = []
        props = dict(boxstyle='round', facecolor='white', alpha=0.6)

        for i_ax, i in enumerate(np.argsort(self.ms_cube.ru)):
            ax = axs.flatten()[i_ax]
            txt = '%.2f / %s - %s' % (self.ms_cube.ru[i] / self.lamb, stat_names[self.ms_cube.ant1[i]]
                                      [3:], stat_names[self.ms_cube.ant2[i]][3:])

            if np.alltrue(self.ms_cube.data[:, :, i, 0].mask):
                all_noise_levels.append((np.nan, np.nan))
                ax.text(0.05, 0.95, txt, transform=ax.transAxes, va='top', ha='left', bbox=props)
                continue

            mean = np.mean(self.all_ps_dt[:, :, i] / 4.)

            ax.plot(self.delay, np.ma.mean(self.all_ps_v[:, :, i], axis=1))
            ax.plot(self.delay, np.ma.mean(self.all_ps_i[:, :, i], axis=1))
            ax.axvline(self.horizon[i], ls='--', c=utils.black)
            ax.axvline(- self.horizon[i], ls='--', c=utils.black)
            ax.axhline(mean, ls='--', c=utils.black)
            ax.set_yscale('log')
            ax.set_xlim(-4, 4)

            noise_r_i = np.mean(self.all_ps_i[(abs(self.delay) > 1.2 * self.horizon[i]) & (abs(self.delay) < 4), :, i]) / mean
            noise_r_v = np.mean(self.all_ps_v[(abs(self.delay) > 1.2 * self.horizon[i]) & (abs(self.delay) < 4), :, i]) / mean
            all_noise_levels.append((noise_r_i, noise_r_v))

            color = 'black'

            txt += '\n%s: I:%.1f V:%.1f' % (i, noise_r_i, noise_r_v)
            ax.text(0.05, 0.95, txt, transform=ax.transAxes, va='top', ha='left', bbox=props, color=color)

        fig.tight_layout(pad=0)
        fig.savefig(plot_dir + '/all_delay_ps_iv.pdf')


class VisFlagger(object):

    def __init__(self, ms_cube, ms_file, ntime_avg):
        self.ms_cube = ms_cube
        self.ms_file = ms_file
        self.ntime_avg = ntime_avg
        self.new_flags = np.zeros_like(self.ms_cube.data.mask)

        self.m_vis_i, self.m_vis_v, self.m_vis_dt = self._get_stokes(ntime_avg=ntime_avg)

        self.delay = utils.get_delay(self.ms_cube.freq * 1e-6, half=False)

        freq = self.ms_cube.freq.mean()
        self.lamb = const.c.value / freq
        self.horizon = utils.get_wedge_delay(np.radians(90), self.ms_cube.bu / self.lamb, freq) * 1e6

    @staticmethod
    def load_from_file(ms_file, ntime_avg, data_col='DATA', umin=50, umax=600):
        ms_cube = msutils.MsDataCube.load(ms_file, umin, umax, data_col, n_time_avg=1)
        
        return VisFlagger(ms_cube, ms_file, ntime_avg)

    def _get_stokes(self, ntime_avg=50):
        m_vis_dt = self.ms_cube.data_dt[:, :, :, 0]
        m_vis_v = 0.5 * (-1j * (self.ms_cube.data[:, :, :, 1] - self.ms_cube.data[:, :, :, 2]))
        m_vis_i = 0.5 * (self.ms_cube.data[:, :, :, 0] + self.ms_cube.data[:, :, :, 3])

        m_vis_i, m_vis_i_n = msutils.mean_consecutive(m_vis_i, axis=1, n=ntime_avg, return_n=True)
        m_vis_i = m_vis_i * np.sqrt(m_vis_i_n)

        m_vis_dt, m_vis_dt_n = msutils.mean_consecutive(m_vis_dt, axis=1, n=ntime_avg, return_n=True)
        m_vis_dt = m_vis_dt * np.sqrt(m_vis_dt_n)

        m_vis_v, m_vis_v_n = msutils.mean_consecutive(m_vis_v, axis=1, n=ntime_avg, return_n=True)
        m_vis_v = m_vis_v * np.sqrt(m_vis_v_n)

        return m_vis_i, m_vis_v, m_vis_dt

    def _get_ps(self, window_fct='boxcar', wedge_factor=1.2, delay_max=4, hpass_filter=True, hpass_n_chan=20):
        all_ps_dt = make_tf(self.m_vis_dt.filled(0), self.ms_cube.freq, window_fct=window_fct)
        if hpass_filter:
            all_ps_i = make_tf(hpass_flag(self.m_vis_i, n_chan=hpass_n_chan).filled(0), self.ms_cube.freq, window_fct=window_fct)
        else:
            all_ps_i = make_tf(self.m_vis_i.filled(0), self.ms_cube.freq, window_fct=window_fct)

        wedge_mask = np.array([(abs(self.delay) > wedge_factor * self.horizon[i]) & (abs(self.delay) < delay_max) for i in  range(all_ps_i.shape[2])]).T
        wedge_mask = np.repeat(wedge_mask[:, None, :], all_ps_i.shape[1], axis=1)
        all_ps_i_m = np.ma.array(all_ps_i, mask=~wedge_mask[:, None, :])

        return all_ps_i_m, all_ps_dt

    def set_flag(self, new_flags):
        self.ms_cube.data.mask = (self.ms_cube.data.mask + new_flags).astype(bool)
        self.m_vis_i, self.m_vis_v, self.m_vis_dt = self._get_stokes(ntime_avg=self.ntime_avg)

    def save_flag(self):
        self.ms_cube.save_flag(self.ms_file, self.ms_cube.data.mask)

    def get_baseline_pair(self, i):
        return self.ms_cube.ant_name[self.ms_cube.ant1[i]], self.ms_cube.ant_name[self.ms_cube.ant2[i]]

    def get_baseline_pairs(self, idx):
        return [self.get_baseline_pair(i) for i in idx]

    def plot_amp_phase(self, baseline_idx, delay_max=4, stokes='I', window_fct='boxcar', hpass_filter=True, hpass_n_chan=20):
        i = baseline_idx
        
        if stokes == 'I':
            if hpass_filter:
                a = hpass_flag(self.m_vis_i[:, :, i], n_chan=hpass_n_chan)
            else:
                a = self.m_vis_i[:, :, i]
        elif stokes == 'V':
            a = self.m_vis_v[:, :, i]
        else:
            print('Wrong Stokes parameters')
            return None

        fig, (ax1, ax2, ax4, ax3) = plt.subplots(ncols=4, figsize=(20, 8))

        extent = [0, 1, self.ms_cube.freq[0] * 1e-6, self.ms_cube.freq[-1] * 1e-6]
        ax1.imshow(np.abs(a), aspect='auto', extent=extent)
        ax2.imshow(np.angle(a), aspect='auto', extent=extent, vmin=-np.pi, vmax=np.pi)

        ax1.set_ylabel('Frequency [ MHz]')
        ax2.set_ylabel('Frequency [ MHz]')
        ax1.set_xlabel('Time')
        ax2.set_xlabel('Time')

        ax1.set_title('Amplitude')
        ax2.set_title('Phase')

        ps = make_tf(a.filled(0), self.ms_cube.freq, window_fct=window_fct)
        m = np.isfinite(ps.data)
        if m.sum() > 0:
            vmin= None
            vmax= None
        else:
            vmin = vmax = 10

        extent = [0, 1, self.delay[0], self.delay[-1]]
        ax3.imshow(np.angle(ps), aspect='auto', extent=extent, vmin=-np.pi, vmax=np.pi)
        ax3.axhline(-self.horizon[i], c='black')
        ax3.axhline(self.horizon[i], c='black')
        ax4.imshow(np.abs(ps), aspect='auto', extent=extent, norm=mpl.colors.LogNorm(vmin, vmax))
        ax4.axhline(-self.horizon[i], c='black')
        ax4.axhline(self.horizon[i], c='black')
        ax3.set_ylabel('Delay [us]')
        ax4.set_ylabel('Delay [us]')
        ax3.set_xlabel('Time')
        ax4.set_xlabel('Time')

        ax3.set_title('Phase')
        ax4.set_title('Amplitude')
        
        a1, a2 = self.get_baseline_pair(i)
        fig.suptitle(f'{a1} - {a2} | {self.ms_cube.ru[i] / self.lamb:.1f} lambda', y=0.985)

        ax3.set_ylim(- delay_max, delay_max)
        ax4.set_ylim(- delay_max, delay_max)
        
        return fig

    def flag_time(self, flag_time_threshold=0.3):
        s = self.ms_cube.data.shape
        mask_freqs = (self.ms_cube.data.mask.sum(axis=(0, 3)) > flag_time_threshold * (s[0] * s[3]))[None, :, :, None]
        percentile_flag = 100 * mask_freqs.sum() / mask_freqs.size
        print(f'-> Time/freq flagging with threshold {flag_time_threshold}: {percentile_flag:.2f} % flagged')
        
        return mask_freqs

    def flag_baseline(self, flag_baseline_threshold=0.8):
        s = self.ms_cube.data.shape
        r_flag = self.ms_cube.data.mask.sum(axis=(0, 1, 3)) / (s[0] * s[1] * s[3])
        mask_baseline = (r_flag > flag_baseline_threshold)[None, None, :, None]
        percentile_flag = 100 * mask_baseline.sum() / mask_baseline.size
        print(f'-> Baseline flagging with threshold {flag_baseline_threshold}: {percentile_flag:.2f} % flagged')
        print('Baseline affected:')
        idx = np.where((r_flag > flag_baseline_threshold) & (r_flag < 1))[0]
        for (a1, a2), i in zip(self.get_baseline_pairs(idx), idx):
            print(f'{a1} - {a2} ({i}; {self.ms_cube.ant1[i]} - {self.ms_cube.ant2[i]})')

        return mask_baseline

    def flag_time_freq(self, n_sigma=5, hpass_n_chan=4, do_plot=False, stokes='I'):
        w = self.ms_cube.weights.copy()
        w[self.ms_cube.data.mask] = 0

        w_avg = msutils.mean_consecutive(w[:, :, :, 0], axis=1, n=self.ntime_avg)

        if stokes == 'I':
            a = self.m_vis_i
        elif stokes == 'V':
            a = self.m_vis_v
        else:
            raise ValueError(f"Invalid Stokes parameter: {stokes}. Only 'I' and 'V' are supported.")

        ps_m = hpass_flag(a, n_chan=hpass_n_chan)

        score = abs(ps_m * w_avg).mean(axis=2)
        masked_score = astats.sigma_clip(score, sigma=n_sigma, stdfunc=astats.mad_std, maxiters=10)

        fig = None
        if do_plot:
            fig, (ax1, ax2, ax3) = plt.subplots(ncols=3, figsize=(20, 8), sharey=True)
            extent = [0, 1, self.ms_cube.freq[0] * 1e-6, self.ms_cube.freq[-1] * 1e-6]

            factor = np.quantile(score, 0.999) / np.median(score)
            vmin = 1 / factor * np.median(score)
            vmax = factor * np.median(score)

            im = ax1.imshow(score, aspect='auto', norm=mpl.colors.LogNorm(vmax=vmax, vmin=vmin), extent=extent)
            plt.colorbar(im, ax=ax1)
            ax1.set_title('Spectra before flagging')

            im = ax2.imshow(masked_score, aspect='auto', norm=mpl.colors.LogNorm(vmax=vmax, vmin=vmin), extent=extent)
            plt.colorbar(im, ax=ax2)
            ax2.set_title('Spectra after flagging')

            m_vis_flag = msutils.mean_consecutive(self.ms_cube.data.mask[:, :, :, 0], axis=1, n=self.ntime_avg)
            im = ax3.imshow(m_vis_flag.mean(axis=2), aspect='auto', vmax=1, vmin=0, extent=extent)
            plt.colorbar(im, ax=ax3)
            ax3.set_title('Flag fraction before flagging')

            ax1.set_ylabel('Frequency [ MHz]')
            ax1.set_xlabel('Time')
            ax2.set_xlabel('Time')
            ax3.set_xlabel('Time')

            fig.tight_layout()

        idx = list(np.linspace(0, masked_score.shape[1] - 1, len(self.ms_cube.time)).astype(int))
        new_flags = masked_score.mask[:, idx][:, :, None, None]

        p_old = self.ms_cube.data.mask.mean() * 100
        p_new = (self.ms_cube.data.mask | new_flags).mean() * 100

        print(f'-> Time/freq flagging with threshold {n_sigma}: before:{p_old:.2f} % flagged, after:{p_new:.2f} % flagged')

        return new_flags, masked_score, fig

    def flag_freqs_band(self, freqs_match, freqs_filter, n_sigma=5, do_plot=False, stokes='I', hpass_filter=False, hpass_n_chan=20):
        new_flags = np.zeros_like(self.ms_cube.data.mask)
        
        if stokes == 'I':
            a = self.m_vis_i
        elif stokes == 'V':
            a = self.m_vis_v
        else:
            raise ValueError(f"Invalid Stokes parameter: {stokes}. Only 'I' and 'V' are supported.")

        if hpass_filter:
            a = hpass_flag(a, n_chan=hpass_n_chan).filled(0)
        a = abs(a)

        idx_filter = (self.ms_cube.freq >= freqs_filter[0]) & ((self.ms_cube.freq <= freqs_filter[1]))
        idx_match = (self.ms_cube.freq >= freqs_match[0]) & ((self.ms_cube.freq <= freqs_match[1]))

        mean_match = np.ma.median(a[idx_match, :, :], axis=(0, 1))
        mean_no_match = np.ma.median(a[~idx_filter, :, :], axis=(0, 1))
        std_no_match = np.ma.std(np.ma.mean(a[~idx_filter, :, :], axis=1), axis=0)

        score = abs(mean_match - mean_no_match)  / std_no_match
        
        masked_score = astats.sigma_clip(score, sigma=n_sigma, stdfunc=astats.mad_std)
        mask = masked_score.mask & (score > 0)

        new_flags[idx_filter, :, :, :] = mask[None, None, :, None]
        percentile_flag = 100 * new_flags.sum() / new_flags.size
        print(f'-> Freqs band {freqs_filter[0]} - {freqs_filter[1]} flagging with n_sigma > {n_sigma}: {percentile_flag:.2f} % flagged')

        fig = None
        if do_plot:
            fig, ax = plt.subplots()
            ax.scatter(self.ms_cube.ru / self.lamb, score, marker='+')
            ax.scatter(self.ms_cube.ru[mask] / self.lamb, score[mask], marker='x', c='red', s=10)
            ax.set_xlabel('Baseline [lambda]')
            ax.set_ylabel('Score')

        print('Baseline affected:')
        idx = np.where(mask)[0]
        for (a1, a2), i in zip(self.get_baseline_pairs(idx), idx):
            print(f'{a1} - {a2} ({i}; {self.ms_cube.ant1[i]} - {self.ms_cube.ant2[i]})')

        return new_flags, masked_score, fig

    def flag_delay_time_outliers(self, n_sigma=5, window_fct='boxcar', wedge_factor=1.2, delay_max=4,
                                 hpass_filter=True, hpass_n_chan=20, do_plot=False):
        all_ps_i_m, all_ps_dt = self._get_ps(window_fct=window_fct, wedge_factor=wedge_factor, delay_max=delay_max,
                                             hpass_filter=hpass_filter, hpass_n_chan=hpass_n_chan)
        all_ps_i_m = np.abs(all_ps_i_m)
        max_to_std = np.ma.max(all_ps_i_m, axis=0) / np.ma.std(all_ps_i_m, axis=(0, 1))

        masked_max_to_std = astats.sigma_clip(max_to_std, sigma=n_sigma, stdfunc=astats.mad_std)
        mask = masked_max_to_std.mask & (masked_max_to_std.data > 0)

        fig = None
        if do_plot:
            fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(9, 4), sharey=True)

            im = ax1.imshow(max_to_std, vmax=10, vmin=0, aspect='auto')
            plt.colorbar(im, ax=ax1)

            im = ax2.imshow(masked_max_to_std, vmax=10, vmin=0, aspect='auto')
            plt.colorbar(im, ax=ax2)
            
            fig.tight_layout()

        idx = list(np.linspace(0, masked_max_to_std.shape[0] - 1, len(self.ms_cube.time)).astype(int))
        new_flags = masked_max_to_std.mask[idx][None, :, :, None]

        percentile_flag = 100 * mask.sum() / mask.size
        print(f'-> Delay time outliers flagging with n_sigma {n_sigma}: {percentile_flag:.2f} % flagged')

        return new_flags, masked_max_to_std, fig

    def flag_delay_baseline_outliers(self, n_sigma=5, window_fct='boxcar', wedge_factor=1.2, delay_max=4,
                                     hpass_filter=True, hpass_n_chan=20, do_plot=False, max_th=2.5, min_th=1.8):
        all_ps_i_m, all_ps_dt = self._get_ps(window_fct=window_fct, wedge_factor=wedge_factor, delay_max=delay_max,
                                             hpass_filter=hpass_filter, hpass_n_chan=hpass_n_chan)
        all_ps_i_m = np.ma.masked_equal(all_ps_i_m, 0)
        all_ps_dt = np.ma.masked_equal(all_ps_dt, 0)
        ratio_med_abs = np.ma.median(abs(all_ps_i_m), axis=1).max(axis=0) / np.ma.median(np.ma.mean(abs(0.5 * all_ps_dt), axis=1), axis=0)

        _, l_th, u_th = astats.sigma_clip(ratio_med_abs, sigma=n_sigma, sigma_lower=20, stdfunc=astats.mad_std, maxiters=10, 
                                                 masked=False, return_bounds=True)
        threshold = np.clip(u_th, min_th, max_th)
        print(f'Threshold: {threshold:.2f} ({u_th} before clipping {max_th}/{min_th})')
        mask = ratio_med_abs > threshold
        masked_ratio_med_abs = np.ma.array(ratio_med_abs, mask=mask)

        fig = None
        if do_plot:
            fig, ax = plt.subplots()
            ax.scatter(self.ms_cube.ru / self.lamb, ratio_med_abs, marker='o')
            ax.scatter(self.ms_cube.ru[mask] / self.lamb, ratio_med_abs[mask], marker='x', c='red', s=10)
            ax.set_xlabel('Baseline [lambda]')
            ax.set_ylabel('Ratio')

        new_flags = mask[None, None, :, None]

        percentile_flag = 100 * new_flags.sum() / new_flags.size
        print(f'-> Delay baseline outliers flagging with n_sigma {n_sigma}: {percentile_flag:.2f} % flagged')

        print('Baseline affected:')
        idx = np.where(mask & (ratio_med_abs < 1e10))[0]
        for (a1, a2), i in zip(self.get_baseline_pairs(idx), idx):
            print(f'{a1} - {a2} ({i}; {self.ms_cube.ant1[i]} - {self.ms_cube.ant2[i]})')

        return new_flags, ratio_med_abs, mask, fig


def load_settings_with_defaults(file_s, file_d):
    c_s = attrmap.AttrMap(toml.load(file_s))
    c_d = attrmap.AttrMap(toml.load(file_d))
    
    return c_d + c_s


def apply_vis_filter(ms_file, config_file, plot_dir=None, dry_run=False):
    do_plot = (plot_dir is not None)

    default_config_file = os.path.join(TEMPLATE_DIR, 'default_vis_flagger_config.toml')
    c_s = load_settings_with_defaults(config_file, default_config_file)

    ms_cube = msutils.MsDataCube.load(ms_file, c_s.umin, c_s.umax, c_s.data_col, n_time_avg=1)
    vis_flagger = VisFlagger(ms_cube, ms_file, c_s.n_time_avg)

    if 'flag_time_threshold' in c_s.filters:
        new_flags = vis_flagger.flag_time(c_s.flag_time_threshold)
        vis_flagger.set_flag(new_flags)

    if 'flag_baseline_threshold' in c_s.filters:
        new_flags = vis_flagger.flag_baseline(c_s.flag_baseline_threshold)
        vis_flagger.set_flag(new_flags)

    if 'flag_time_freq_outliers' in c_s.filters:
        s = c_s.flag_time_freq_outliers
        new_flags, _, fig = vis_flagger.flag_time_freq(do_plot=do_plot, n_sigma=s.n_sigma,
                                                       hpass_n_chan=s.hpass_n_chan, stokes=s.stokes)
        vis_flagger.set_flag(new_flags)

        if do_plot:
            fig.savefig(f'{plot_dir}/flag_time_freq_outliers.png')

    if 'flag_freqs_band' in c_s.filters:
        for band, s in c_s.flag_freqs_band.items():
            f_f = s['freqs_filter']
            f_m = s['freqs_match']
            hpass_filter = s.get('hpass_filter', False)
            new_flags, masked_score, fig = vis_flagger.flag_freqs_band(f_m, f_f, n_sigma=s['n_sigma'], stokes=s['stokes'], 
                                                                       do_plot=do_plot, hpass_filter=hpass_filter)
            mask = masked_score.mask & (masked_score > 0)
        
            if do_plot:
                fig.savefig(f'{plot_dir}/flag_freqs_band_{band}.png')
                for i in np.where(mask)[0]:
                    fig = vis_flagger.plot_amp_phase(i, stokes='I', window_fct='hann')
                    fig.savefig(f'{plot_dir}/flag_freqs_band_{band}_{i}.png')
                    plt.close(fig)

            vis_flagger.set_flag(new_flags)

            if do_plot:
                for i in np.where(mask)[0]:
                    fig = vis_flagger.plot_amp_phase(i, stokes='I', window_fct='hann')
                    fig.savefig(f'{plot_dir}/flag_freqs_band_after_{band}_{i}.png')
                    plt.close(fig)

    if 'flag_delay_time_outliers' in c_s.filters:
        s = c_s.flag_delay_time_outliers
        new_flags, masked_max_to_std, fig = vis_flagger.flag_delay_time_outliers(do_plot=do_plot, n_sigma=s.n_sigma, 
                                                                                 window_fct=s.window_fct, wedge_factor=s.wedge_factor,
                                                                                 hpass_filter=s.hpass_filter)
        vis_flagger.set_flag(new_flags)

        if do_plot:
            fig.savefig(f'{plot_dir}/flag_delay_time_outliers.png')

    if 'flag_delay_baseline_outliers' in c_s.filters:
        s = c_s.flag_delay_baseline_outliers
        new_flags, ratio_med_abs, mask, fig = vis_flagger.flag_delay_baseline_outliers(do_plot=do_plot, n_sigma=s.n_sigma, 
                                                                                       window_fct=s.window_fct, wedge_factor=s.wedge_factor,
                                                                                       max_th=s.max_threshold, min_th=s.min_threshold,
                                                                                       hpass_filter=s.hpass_filter)
        
        if do_plot:
            fig.savefig(f'{plot_dir}/flag_delay_baseline_outliers.png')
            for i in np.where(mask & (ratio_med_abs < 1e10))[0]:
                fig = vis_flagger.plot_amp_phase(i, stokes='I', window_fct='hann')
                fig.savefig(f'{plot_dir}/flag_delay_baseline_outliers_{i}.png')
                plt.close(fig)

        vis_flagger.set_flag(new_flags)

    if not dry_run:
        vis_flagger.save_flag()
