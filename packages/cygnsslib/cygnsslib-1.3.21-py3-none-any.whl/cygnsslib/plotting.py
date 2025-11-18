from collections import defaultdict
from datetime import datetime
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
from mpl_toolkits.axes_grid1 import make_axes_locatable
from typing import Optional
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd


def axis_formatter_degree(x, pos): return f'{x:-0.0f}'.replace('-', u'\u2212')+ '$^\mathrm{o}$'
try:
    mpl.use('Qt5Agg')
except Exception:
    pass

sel_colormap = 'jet'  # matplotlib default is 'viridis'
default_fig_width = 8  # default figure width
plt_font_size = 20  # font size
plt_title = True  # plot figures titles
plot_db_range = 20  # default dynamic range of dB plots
default_save_type = ['png']  # default save image types
ddm_plt_default_delay_axis = 'x'

SMALL_SIZE = plt_font_size - 2
MEDIUM_SIZE = plt_font_size
BIGGER_SIZE = plt_font_size
plt.rc('font', size=SMALL_SIZE)  # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)  # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)  # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

mpl.rcParams['font.size'] = plt_font_size
mpl.rcParams['legend.fontsize'] = 'large'
mpl.rcParams['figure.titlesize'] = 'medium'
mpl.rcParams["axes.unicode_minus"] = True

def lin2db(val):
    if isinstance(val, np.ndarray):
        val[val<=0.0] = np.nan
    else:
        if val <= 0.0:
            val = np.nan
    return 10.0 * np.log10(val)
def axis_formatter_no_frac(x, pos): return f'{x:-0.0f}'.replace('-', u'\u2212')

def format_range_val(start, finish, unit=''):
    return f'[{start}{unit},{finish}{unit}]'.replace('-', u'\u2212')
def pwr2db_threshold(power_linear, dynamic_range_db=None):
    """

    change power from linear two dB with a minimum threshold

    :param power_linear: power in linear scale
    :type power_linear: np.array
    :param dynamic_range_db: dynamic range in dB any value below the maximum by this is set to max - scale
    :type dynamic_range_db: float
    :return: power in dB scale
    :rtype: np.array
    """
    if dynamic_range_db is None:
        dynamic_range_db = plot_db_range

    threshold = np.nanmax(power_linear) * 10 ** (-dynamic_range_db / 10)
    power_db = 10.0 * np.log10(np.where(power_linear < threshold, threshold, power_linear))
    power_db = np.nan_to_num(power_db, nan=np.nanmin(power_db))
    return power_db


def plot_single_ddm(image, title, img_save_name, fig_out_folder, tf_save_fig=True, img_ext=None, fig_width=None,
                    plt_delay_axis=None, cbar_min_max=None, fig_save_types: Optional[list[str]] = None, cbar_title=None,
                    delay_scale=None, dopp_scale=None, plt_db_tf = True):
    """

    plot a single DDM

    :param image: DDM [dim 0: delay, dim 1: Doppler]
    :type image: np.array
    :param title: plot title
    :type title: str
    :param img_save_name: image save name
    :type img_save_name: str
    :param fig_out_folder: image saving folder
    :type fig_out_folder: str
    :param tf_save_fig: save the figure?
    :type tf_save_fig: bool
    :param img_ext: extend of the image
    :type img_ext: tuple
    :param fig_width: figure width, if None default_fig_width is selected
    :type fig_width: int or float
    :param plt_delay_axis: where the delay axis? select 'x' or 'y'
    :type plt_delay_axis: str or None
    :return: figure handle
    :rtype: plt.figure
    """
    plt_bar_title = True
    if delay_scale is None:
        delay_scale = 1.0
    if dopp_scale is None:
        dopp_scale = 1.0
    if cbar_title is None:
        cbar_title = 'Reflectivity [dB]'
    if plt_delay_axis is None:
        plt_delay_axis = ddm_plt_default_delay_axis
    if fig_width is None:
        fig_width = default_fig_width
    if plt_delay_axis.lower() == 'x':
        image = np.transpose(image)

    delay_axis = 1 if (plt_delay_axis.lower() == 'x') else 0
    dopp_axis = 0 if (plt_delay_axis.lower() == 'x') else 1
    num_delay = int(image.shape[delay_axis] * delay_scale / 2)
    num_dopp = int(image.shape[dopp_axis] * dopp_scale / 2)
    if plt_delay_axis.lower() == 'x':
        fig_size = (fig_width, np.round(fig_width * num_dopp / num_delay, decimals=2))
        y_label = 'Doppler bin'
        x_label = 'Delay bin'
        if img_ext is None:  # image ext (left, right, bottom, top)
            img_ext = (-num_delay-0.5*delay_scale,
                       num_delay+0.5*delay_scale,
                       -num_dopp-0.5*dopp_scale,
                       num_dopp+0.5*dopp_scale)
    elif plt_delay_axis.lower() == 'y':
        fig_size = (np.round(fig_width * num_dopp / num_delay, decimals=2), fig_width * 0.9)
        x_label = 'Doppler bin'
        y_label = 'Delay bin'
        if img_ext is None:  # image ext (left, right, bottom, top)
            img_ext = (-num_dopp-0.5,
                       num_dopp+0.5,
                       -num_delay-0.5,
                       num_delay+0.5)
    else:
        raise RuntimeError(f'plt_delay_axis has only two options: x and y, you selected {plt_delay_axis}')

    fig = plt.figure(figsize=fig_size)
    ax = plt.subplot(111)
    im = ax.imshow(image, origin='lower', extent=img_ext, cmap=sel_colormap)
    minor_tick_num = 2
    if cbar_min_max is not None:
        z_min, z_max = cbar_min_max
        if (z_max - z_min) < 15.0:
            z_step = 2
            minor_tick_num = 2
        elif (z_max - z_min) < 30.0:
            z_step = 5
            minor_tick_num = 5
        else:
            z_step = 10
            minor_tick_num = 2
        cbar_ticks = np.arange(z_min, z_max + z_step, z_step)
        im.set_clim(z_min, z_max)
    elif plt_db_tf:
        z_min = np.nanmin(image)
        z_max = np.nanmax(image)
        if (z_max - z_min) < 15.0:
            z_step = 2
            minor_tick_num = 2
        elif (z_max - z_min) < 30.0:
            z_step = 5
            minor_tick_num = 5
        else:
            z_step = 10
            minor_tick_num = 2
        _z_step = np.minimum(5, z_step)
        vmin = np.floor(z_min / _z_step) * _z_step
        vmax = np.ceil(z_max / _z_step) * _z_step
        try:
            cbar_ticks = np.arange(vmin, vmax + z_step, z_step)
        except ValueError:
            print(f'Error in setting cbar, {vmin}, {vmax}')
            cbar_ticks = None

        im.set_clim(vmin, vmax)
    else:
        minor_tick_num = 2
        cbar_ticks = None
    if title and plt_title:  # this in case we want to remove titles for papers
        plt.title(title, fontsize=plt_font_size-2)
    plt.xlabel(x_label, fontsize=plt_font_size)
    plt.ylabel(y_label, fontsize=plt_font_size)
    ax.tick_params(axis='both', which='major', labelsize=plt_font_size)
    if num_delay % 2 != 0:  # odd number
        num_delay += -1
    if num_dopp % 2 != 0:  # odd number
        num_dopp += -1
    delay_step = 2 if num_delay < 10 else 4
    delay_ticks = np.arange(-num_delay, stop=num_delay + delay_step, step=delay_step).astype(int)
    dopp_step = 2 if num_dopp < 10 else 4
    dopp_ticks = np.arange(-num_dopp, stop=num_dopp + dopp_step, step=dopp_step).astype(int)
    if plt_delay_axis.lower() == 'x':
        ax.set_xticks(delay_ticks)
        ax.set_yticks(dopp_ticks)
    else:
        ax.set_yticks(delay_ticks)
        ax.set_xticks(dopp_ticks)
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))

    # create an axes on the right side of ax. The width of cax will be 5%
    # of ax and the padding between cax and ax will be fixed at 0.05 inch.
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    cbar = plt.colorbar(im, cax=cax)
    # cbar = plt.colorbar(fraction=c_fraction, pad=0.02)
    cbar.ax.tick_params(labelsize=plt_font_size)
    cbar.ax.yaxis.set_major_formatter(axis_formatter_no_frac)
    # Turn on minor ticks
    if cbar_ticks is not None:
        cbar.set_ticks(cbar_ticks)
    cbar.minorticks_on()
    cbar.ax.yaxis.set_minor_locator(AutoMinorLocator(minor_tick_num))  # For vertical colorbar

    if plt_bar_title:
        cbar.ax.set_ylabel(cbar_title, rotation=270, fontsize=plt_font_size, labelpad=plt_font_size)
    plt.tight_layout()
    plt.tight_layout()
    plt.tight_layout()
    save_figure(fig, fig_out_folder, img_save_name, tf_save_fig, fig_save_types)
    return fig


# Function to plot data for varying sp_inc_angle with fixed other parameters
def plot_varying_sp_inc_angle(grouped_data, folder_path, img_tag, fig_save_types):
    for smap_sm_group, sc_alt_groups in grouped_data.items():
        for sc_alt_group, sp_inc_angle_groups in sc_alt_groups.items():
            list_az_angles = []
            for sp_inc_angle_group, sc_az_angle_groups in sp_inc_angle_groups.items():
                for sc_az_angle_group, items in sc_az_angle_groups.items():
                    if sc_az_angle_group not in list_az_angles:
                        list_az_angles.append(sc_az_angle_group)
            list_az_angles.sort()
            for sc_az_angle_group in list_az_angles:
                fig = plt.figure()
                ax = plt.subplot(111)
                i_plt = 0
                for sp_inc_angle_group, sc_az_angle_items in sp_inc_angle_groups.items():
                    if sc_az_angle_group in sc_az_angle_items:
                        items = sc_az_angle_items[sc_az_angle_group]

                        timestamps = [datetime.fromisoformat(item['ddm_timestamp_utc_str'][:-3]) for item in items]
                        reflectivity_peaks = [item['reflectivity_peak'] for item in items]

                        if len(reflectivity_peaks) < 2:
                            continue
                        # Sort data by timestamps
                        sorted_data = sorted(zip(timestamps, reflectivity_peaks))
                        sorted_timestamps, sorted_reflectivity_peaks = zip(*sorted_data)
                        peak_refl = lin2db(np.array(sorted_reflectivity_peaks))
                        ax.plot(sorted_timestamps, peak_refl, marker='o', linestyle='', label=format_range_val(sp_inc_angle_group, sp_inc_angle_group+5, '$^\mathrm{o}$'))
                        i_plt += 1

                if i_plt == 0:
                    plt.close(fig)
                    continue
                ax.set_xlabel('Timestamp (UTC)', fontsize=plt_font_size)
                ax.set_ylabel('Peak reflectivity [dB]', fontsize=plt_font_size)
                ax.grid()
                # Determine the tick range for y-axis
                y_min, y_max = plt.ylim()
                # Define ticks with a step of y-axis
                if (y_max - y_min) < 15.0:
                    y_step = 2
                    num_minor_ticks = 2
                elif (y_max - y_min) < 30.0:
                    y_step = 5
                    num_minor_ticks = 5
                else:
                    y_step = 10
                    num_minor_ticks = 2

                y_ticks = np.arange(np.floor(y_min/y_step) * y_step, np.ceil(y_max/y_step) * y_step + y_step, y_step)
                ax.set_yticks(y_ticks)
                ax.yaxis.set_minor_locator(AutoMinorLocator(num_minor_ticks))

                # plt.title(f'Reflectivity Peak over Time for smap_sm: {smap_sm_group}, sc_alt: {sc_alt_group}, sc_az_angle: {sc_az_angle_group}')
                legend_vbox = 1.5

                plt.legend(title='$\\theta_\mathrm{i}$', loc="upper center", bbox_to_anchor=(.5, legend_vbox), ncol=3,
                           fontsize=plt_font_size - (4 if plt_font_size > 16 else 0), handletextpad=0.3, borderpad=0.3, labelspacing=0.3, columnspacing=1.0, markerscale=1.5)
                plt.xticks(rotation=45)
                sc_az_angle_group_str = str(sc_az_angle_group) if sc_az_angle_group > 0.0 else 'n' + str(abs(sc_az_angle_group))
                img_name = img_tag + f'_peak_refl_vary_inc_angle_sm_{int(smap_sm_group * 100):d}_alt_{sc_alt_group}_az_{sc_az_angle_group_str}'
                save_figure(fig, folder_path, img_name, fig_save_types=fig_save_types)
                plt.close(fig)


# Function to plot data for varying sc_az_angle with fixed other parameters
def plot_varying_sc_az_angle(grouped_data, folder_path, img_tag, fig_save_types):
    for smap_sm_group, sc_alt_groups in grouped_data.items():
        for sc_alt_group, sp_inc_angle_groups in sc_alt_groups.items():
            for sp_inc_angle_group, sc_az_angle_groups in sp_inc_angle_groups.items():
                fig = plt.figure()
                ax = plt.subplot(111)
                i_plt = 0
                for sc_az_angle_group, items in sc_az_angle_groups.items():
                    timestamps = [datetime.fromisoformat(item['ddm_timestamp_utc_str'][:-3]) for item in items]
                    reflectivity_peaks = [item['reflectivity_peak'] for item in items]

                    # Sort data by timestamps
                    sorted_data = sorted(zip(timestamps, reflectivity_peaks))
                    sorted_timestamps, sorted_reflectivity_peaks = zip(*sorted_data)
                    peak_refl = lin2db(np.array(sorted_reflectivity_peaks))
                    ax.plot(sorted_timestamps, peak_refl, marker='o', linestyle='', label=format_range_val(sp_inc_angle_group, sc_az_angle_group+5, '$^\mathrm{o}$'))
                    i_plt += 1
                if i_plt == 0:
                    plt.close(fig)
                    continue

                ax.set_xlabel('Timestamp (UTC)')
                ax.set_ylabel('Peak reflectivity [dB]')
                ax.grid()

                # Determine the tick range for y-axis
                y_min, y_max = plt.ylim()
                # Define ticks with a step of y-axis
                if (y_max - y_min) < 15.0:
                    y_step = 2
                    num_minor_ticks = 2
                elif (y_max - y_min) < 30.0:
                    y_step = 5
                    num_minor_ticks = 5
                else:
                    y_step = 10
                    num_minor_ticks = 2

                y_ticks = np.arange(np.floor(y_min/y_step) * y_step, np.ceil(y_max/y_step) * y_step + y_step, y_step)
                ax.set_yticks(y_ticks)
                ax.yaxis.set_minor_locator(AutoMinorLocator(num_minor_ticks))

                # plt.title(f'Reflectivity Peak over Time for smap_sm: {smap_sm_group}, sc_alt: {sc_alt_group}, sp_inc_angle: {sp_inc_angle_group}')
                legend_vbox = 1.5
                plt.legend(title='$\\theta_\mathrm{az}$', loc="upper center", bbox_to_anchor=(.5, legend_vbox), ncol=3,
                           fontsize=plt_font_size - (4 if plt_font_size > 16 else 0), handletextpad=0.3, borderpad=0.3, labelspacing=0.3, columnspacing=1.0, markerscale=1.5)

                plt.xticks(rotation=45)
                plt.tight_layout()
                img_name = img_tag + f'_peak_refl_vary_az_angle_sm_{int(smap_sm_group * 100):d}_alt_{sc_alt_group}_az_{sp_inc_angle_group}'
                save_figure(fig, folder_path, img_name, fig_save_types=fig_save_types)
                plt.close(fig)


# Function to plot data for varying sc_az_angle with fixed other parameters
def plot_reflectivity_x_az_lg_inc_angle(grouped_data, folder_path, img_tag, fig_save_types, db_lim=None, separate_legend=True):
    # clr_list = mpl.rcParams['axes.prop_cycle']
    # clr_list = ['#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fee08b', '#e6f598', '#abdda4', '#66c2a5', '#3288bd', '#5e4fa2']
    clr_list = ["#E5E5E5","#D2D2D2","#BFBFBF","#ACACAC","#999999","#868686","#737373","#5F5F5F","#4C4C4C","#393939","#262626","#131313","#000000"]
    symb_list = ['o', 's', '^']
    save_lim = 3  # save image if number of incidence angles >= savelim
    for smap_sm_group, sc_alt_groups in grouped_data.items():
        if smap_sm_group < 0: # skip soil moisture below 0.
            continue
        for sc_alt_group, sp_inc_angle_groups in sc_alt_groups.items():
            # Sort sp_inc_angle groups before plotting
            sorted_sp_inc_angle_groups = sorted(sp_inc_angle_groups.items(), key=lambda x: x[0])
            num_plt = len([inc_ang for inc_ang, _ in sorted_sp_inc_angle_groups if inc_ang <= 60.0])
            if num_plt < save_lim:
                continue
            n_rows = int(np.ceil(num_plt/3))
            fig_height = _get_fig_height_from_leg_row(n_rows) if not separate_legend else 4.2
            fig = plt.figure(figsize=(6,fig_height))
            ax = plt.subplot(111)
            lines = []
            i_plt = 0
            for sp_inc_angle_group, sc_az_angle_groups in sorted_sp_inc_angle_groups:
                if sp_inc_angle_group > 60.0:  # only plot incidence angles below 60
                    continue
                clr_idx = int(sp_inc_angle_group / 5)
                sc_az_angles = []
                reflectivity_peaks = []

                for sc_az_angle_group, items in sc_az_angle_groups.items():
                    sc_az_angles.extend([item['sc_az_angle'] for item in items])
                    reflectivity_peaks.extend([item['reflectivity_peak'] for item in items])

                # Sort data by sc_az_angles
                sorted_data = sorted(zip(sc_az_angles, reflectivity_peaks))
                sorted_sc_az_angles, sorted_reflectivity_peaks = zip(*sorted_data)
                peak_refl = lin2db(np.array(sorted_reflectivity_peaks))
                l = ax.plot(sorted_sc_az_angles, peak_refl, marker=symb_list[clr_idx % len(symb_list)], linestyle='', color=clr_list[clr_idx % len(clr_list)],
                         label=format_range_val(sp_inc_angle_group, sp_inc_angle_group+5, '$^\mathrm{o}$'))
                lines +=l
                i_plt += 1
            ax.set_xlim([-180, 180])
            xticks = np.arange(-180, 180+90, 90)
            ax.set_xticks(xticks)
            ax.xaxis.set_minor_locator(AutoMinorLocator(2))

            if db_lim is not None:
                ax.set_ylim(db_lim[0], db_lim[1])
            # Determine the tick range for y-axis
            y_min, y_max = plt.ylim()
            # Define ticks with a step of y-axis
            if (y_max - y_min) < 15.0:
                y_step = 2
                num_minor_ticks = 2
            elif (y_max - y_min) < 30.0:
                y_step = 5
                num_minor_ticks = 5
            else:
                y_step = 10
                num_minor_ticks = 2

            y_ticks = np.arange(np.floor(y_min/y_step) * y_step, np.ceil(y_max/y_step) * y_step + y_step, y_step)
            ax.set_yticks(y_ticks)
            ax.yaxis.set_minor_locator(AutoMinorLocator(num_minor_ticks))

            plt.xlabel('Receiver azimuth angle')
            plt.ylabel('Peak reflectivity [dB]')
            ax.xaxis.set_major_formatter(axis_formatter_degree)
            plt.grid()
            if not separate_legend:
                ax.set_position([0.18, 0.14, 0.75, 0.6])  # [left, bottom, width, height] in figure fraction
                legend_vbox = _get_fig_legend_bbox(n_rows)
                plt.legend(title='$\\theta_\mathrm{i}$', loc="upper center", bbox_to_anchor=(.5, legend_vbox), ncol=3,
                           fontsize=plt_font_size - (4 if plt_font_size > 16 else 0), handletextpad=0.0, borderpad=0.3,
                           labelspacing=0.3, columnspacing=0.3, markerscale=1.0)
                fig.set_figheight(_get_fig_height_from_leg_row(n_rows))  # Adjust the total figure height
                plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust rect to leave space for the legend
            else:
                plt.tight_layout()
            img_name = img_tag + f'_peak_refl_vs_az_angle_varying_inc_angle_sm_{int(smap_sm_group * 100):d}_alt_{sc_alt_group}'
            if separate_legend:
                img_name += '_plot'
            save_figure(fig, folder_path, img_name, fig_save_types=fig_save_types)

            if separate_legend:
                # Create a new figure for the legend
                leg_h = 1 + 0.3 * n_rows
                fig_legend = plt.figure(figsize=(5, leg_h))  # Adjust size as needed
                fig_legend.legend(handles=lines, loc='center', title='$\\theta_\mathrm{i}$', ncol=3,
                                  fontsize=plt_font_size - (4 if plt_font_size > 16 else 0), handletextpad=0.0, borderpad=0.3, labelspacing=0.3,
                                  columnspacing=0.3, markerscale=1.0)
                # Turn off axes for the legend-only figure
                plt.axis('off')
                plt.tight_layout()
                img_name = img_name[:-4] + 'legend'
                save_figure(fig_legend, folder_path, img_name, fig_save_types=fig_save_types)
                plt.close(fig_legend)

            plt.close(fig)

def _get_fig_height_from_leg_row(n_rows):
    fig_height = 4.2 + 0.55 * n_rows
    return fig_height
def _get_fig_legend_bbox(n_rows):
    return 1.25 + 0.07 * n_rows
# Function to plot data for varying sc_az_angle with fixed other parameters
def plot_reflectivity_x_sm_lg_inc_angle_all_az(grouped_data, folder_path, img_tag, fig_save_types, db_lim=None, separate_legend=True):
    plt_linear_fit = True
    linter_fit_refl_in_db = True
    save_lim = 3  # save image if number of incidence angles >= savelim
    # clr_list = mpl.rcParams['axes.prop_cycle'].by_key()['color']
    clr_list = ["#E5E5E5","#D2D2D2","#BFBFBF","#ACACAC","#999999","#868686","#737373","#5F5F5F","#4C4C4C","#393939","#262626","#131313","#000000"]
    symb_list = ['o', 's', '^']

    list_alt_vals = []
    list_az_angles = []
    linear_fit_csv_fn = img_tag + f'_linear_fit_sm_refl.csv'
    linear_fit_csv_fp = os.path.join(folder_path, linear_fit_csv_fn)
    for smap_sm_group, sc_alt_groups in grouped_data.items():
        for sc_alt_group, sp_inc_angle_groups in sc_alt_groups.items():
            if sc_alt_group not in list_alt_vals:
                list_alt_vals.append(sc_alt_group)
            for sp_inc_angle_group, sc_az_angle_groups in sp_inc_angle_groups.items():
                if sp_inc_angle_group > 60.0:  # only plot incidence angles below 60
                    continue
                for az_angle_group in sc_az_angle_groups:
                    if az_angle_group not in list_az_angles:
                        list_az_angles.append(az_angle_group)
    linear_fit_data = {'altitude': [],
                       'slope_a1': [],
                       'bias_a0': [],
                       'num_samples': []}
    for alt_val in list_alt_vals:
        smap_sm_values = defaultdict(list)
        sp_inc_angle_values = defaultdict(list)
        reflectivity_peaks = defaultdict(list)

        for az_angle in list_az_angles:
            for smap_sm_group, sc_alt_groups in grouped_data.items():
                if alt_val in sc_alt_groups:
                    sp_inc_angle_groups = sc_alt_groups[alt_val]
                    for sp_inc_angle_group, sc_az_angle_groups in sp_inc_angle_groups.items():
                        if sp_inc_angle_group > 60.0:  # only plot incidence angles below 60
                            continue
                        for sc_az_angle_group, items in sc_az_angle_groups.items():
                            # Extract smap_sm, sp_inc_angle, and reflectivity_peak
                            smap_sm_values[sp_inc_angle_group] += [item['smap_sm'] for item in items if item['smap_sm'] > 0.0]
                            sp_inc_angle_values[sp_inc_angle_group] += [item['sp_inc_angle'] for item in items if item['smap_sm'] > 0.0]
                            reflectivity_peaks[sp_inc_angle_group] += [item['reflectivity_peak'] for item in items if item['smap_sm'] > 0.0]

        num_plt = len(reflectivity_peaks)
        n_rows = int(np.ceil(num_plt/3))
        fig_height = _get_fig_height_from_leg_row(n_rows) if not separate_legend else 4.2
        fig = plt.figure(figsize=(6,fig_height))
        ax = plt.subplot(111)
        i_plt = 0
        lines = []
        if num_plt < save_lim:
            continue

        all_refl = np.concatenate([np.array(_refl) for _refl in reflectivity_peaks.values()])
        all_sm = np.concatenate([np.array(_sm) for _sm in smap_sm_values.values()])
        _sm_lin_fit = np.arange(0, 0.4+0.01,0.01)

        if linter_fit_refl_in_db:
            coef_ = np.polynomial.polynomial.polyfit(all_sm, lin2db(all_refl), 1)
            _refl_lin_fit = coef_[1] * _sm_lin_fit + coef_[0]
        else:
            coef_ = np.polynomial.polynomial.polyfit(all_sm, all_refl, 1)
            _refl_lin_fit = lin2db(coef_[1] * _sm_lin_fit + coef_[0])
        linear_fit_data['altitude'].append(alt_val)
        linear_fit_data['slope_a1'].append(coef_[1])
        linear_fit_data['bias_a0'].append(coef_[0])
        linear_fit_data['num_samples'].append(len(all_refl))
        uniq_inc_angle = sorted(smap_sm_values.keys())
        for sp_inc_angle_group in uniq_inc_angle:
            peak_refl = lin2db(np.array(reflectivity_peaks[sp_inc_angle_group]))
            _sm_vals = smap_sm_values[sp_inc_angle_group]
            clr_idx = int(sp_inc_angle_group/5)
            l = ax.plot(_sm_vals, peak_refl, marker=symb_list[clr_idx % len(symb_list)], linestyle='', color=clr_list[clr_idx % len(clr_list)],
                     label=format_range_val(sp_inc_angle_group, sp_inc_angle_group+5, '$^\mathrm{o}$'))
            i_plt += 1
            lines += l
        if plt_linear_fit:
            l0 = ax.plot(_sm_lin_fit, _refl_lin_fit, linestyle='--', color='b', alpha=0.8, label='Linear fit')
            lines += l0
        plt.xlabel('Soil moisture $[\mathrm{m}^3 \mathrm{m}^{-3}]$')
        plt.xlim([0.0, 0.4])
        x_ticks = np.arange(0, 0.6, 0.1)
        ax.set_xticks(x_ticks)
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))

        if db_lim is not None:
            ax.set_ylim(db_lim[0], db_lim[1])
        # Determine the tick range for y-axis
        y_min, y_max = plt.ylim()
        # Define ticks with a step of y-axis
        if (y_max - y_min) < 15.0:
            y_step = 2
            num_minor_ticks = 2
        elif (y_max - y_min) < 30.0:
            y_step = 5
            num_minor_ticks = 5
        else:
            y_step = 10
            num_minor_ticks = 2
        y_ticks = np.arange(np.floor(y_min/y_step) * y_step, np.ceil(y_max/y_step) * y_step + y_step, y_step)
        ax.set_yticks(y_ticks)
        ax.yaxis.set_minor_locator(AutoMinorLocator(num_minor_ticks))
        plt.ylabel('Peak reflectivity [dB]')
        plt.grid()
        if not separate_legend:
            ax.set_position([0.18, 0.14, 0.75, 0.6])  # [left, bottom, width, height] in figure fraction
            legend_vbox = _get_fig_legend_bbox(n_rows)
            plt.legend(title='$\\theta_\mathrm{i}$', loc="upper center", bbox_to_anchor=(.5, legend_vbox), ncol=3,
                       fontsize=plt_font_size - (4 if plt_font_size > 16 else 0), handletextpad=0.0, borderpad=0.3, labelspacing=0.3, columnspacing=0.3, markerscale=1.0)
            fig.set_figheight(_get_fig_height_from_leg_row(n_rows))  # Adjust the total figure height
            plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust rect to leave space for the legend
        else:
            plt.tight_layout()
        img_name = img_tag + f'_peak_refl_vs_sm_varying_inc_angle_all_az_alt_{alt_val}'
        if separate_legend:
            img_name += '_plot'
        save_figure(fig, folder_path, img_name, fig_save_types=fig_save_types)

        if separate_legend:
            # Create a new figure for the legend
            leg_h = 1 + 0.3 * n_rows
            fig_legend = plt.figure(figsize=(5, leg_h))  # Adjust size as needed
            fig_legend.legend(handles=lines, loc='center', title='$\\theta_\mathrm{i}$', ncol=3,
                              fontsize=plt_font_size - (4 if plt_font_size > 16 else 0), handletextpad=0.0, borderpad=0.3, labelspacing=0.3,
                              columnspacing=0.3, markerscale=1.0)
            # Turn off axes for the legend-only figure
            plt.axis('off')
            plt.tight_layout()
            img_name = img_name[:-4] + 'legend'
            save_figure(fig_legend, folder_path, img_name, fig_save_types=fig_save_types)
            plt.close(fig_legend)

        plt.close(fig)
    pd.DataFrame(linear_fit_data).to_csv(linear_fit_csv_fp, index=False)


# Function to plot data for varying sc_az_angle with fixed other parameters
def plot_reflectivity_x_az_lg_sm(grouped_data, folder_path, img_tag, fig_save_types, db_lim=None):
    # clr_list = mpl.rcParams['axes.prop_cycle']
    # clr_list = ['#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fee08b', '#e6f598', '#abdda4', '#66c2a5', '#3288bd', '#5e4fa2']
    clr_list = ["#E5E5E5","#D2D2D2","#BFBFBF","#ACACAC","#999999","#868686","#737373","#5F5F5F","#4C4C4C","#393939","#262626","#131313","#000000"]
    symb_list = ['o', 's', '^']
    save_lim = 3  # save image if number of incidence angles >= savelim
    list_alt_vals = []
    list_inc_angles = []
    for smap_sm_group, sc_alt_groups in grouped_data.items():
        for sc_alt_group, sp_inc_angle_groups in sc_alt_groups.items():
            if sc_alt_group not in list_alt_vals:
                list_alt_vals.append(sc_alt_group)
            for sp_inc_angle_group, sc_az_angle_groups in sp_inc_angle_groups.items():
                if sp_inc_angle_group not in list_inc_angles:
                    list_inc_angles.append(sp_inc_angle_group)

    sorted_sm_data = sorted(grouped_data.items(), key=lambda x: x[0])
    for alt_val in list_alt_vals:
        for inc_angle in list_inc_angles:
            num_plt = len([sm_val for sm_val, _ in sorted_sm_data if sm_val > 0.0])
            if num_plt <= save_lim:
                continue
            n_rows = int(np.ceil(num_plt/3))
            fig_height = _get_fig_height_from_leg_row(n_rows)
            fig = plt.figure(figsize=(6,fig_height))
            ax = plt.subplot(111)
            i_plt = 0
            plotted_sm_val = []
            lines = []
            for smap_sm_group, sc_alt_groups in sorted_sm_data:
                if smap_sm_group < 0: # skip soil moisture below 0.
                    continue
                clr_idx = int(smap_sm_group / 0.05)

                if alt_val in sc_alt_groups:
                    for sc_alt_group, sp_inc_angle_groups in sc_alt_groups.items():
                        if inc_angle in sp_inc_angle_groups:
                            sc_az_angle_groups =  sp_inc_angle_groups[inc_angle]
                            sc_az_angles = []
                            reflectivity_peaks = []

                            for sc_az_angle_group, items in sc_az_angle_groups.items():
                                sc_az_angles.extend([item['sc_az_angle'] for item in items])
                                reflectivity_peaks.extend([item['reflectivity_peak'] for item in items])

                            # Sort data by sc_az_angles
                            sorted_data = sorted(zip(sc_az_angles, reflectivity_peaks))
                            sorted_sc_az_angles, sorted_reflectivity_peaks = zip(*sorted_data)
                            peak_refl = lin2db(np.array(sorted_reflectivity_peaks))
                            sm_rounded = int(np.round(smap_sm_group * 100)) / 100.0
                            upp_lim_grp_sm = int(np.round((sm_rounded+0.05) * 100)) / 100.0
                            l1 = plt.plot(sorted_sc_az_angles, peak_refl, marker=symb_list[clr_idx % len(symb_list)], linestyle='', color=clr_list[clr_idx % len(clr_list)],
                                     label=format_range_val(sm_rounded, upp_lim_grp_sm, ''))
                            if sm_rounded not in plotted_sm_val:
                                plotted_sm_val.append(sm_rounded)
                                lines += l1
                                i_plt += 1
            if i_plt <= save_lim:
                plt.close(fig)
                continue
            ax.set_xlim([-180, 180])
            xticks = np.arange(-180, 180+90, 90)
            ax.xaxis.set_minor_locator(AutoMinorLocator(2))

            if db_lim is not None:
                ax.set_ylim(db_lim[0], db_lim[1])
            # Determine the tick range for y-axis
            y_min, y_max = plt.ylim()

            # Define ticks with a step of y-axis
            if (y_max - y_min) < 15.0:
                y_step = 2
                num_minor_ticks = 2
            elif (y_max - y_min) < 30.0:
                y_step = 5
                num_minor_ticks = 5
            else:
                y_step = 10
                num_minor_ticks = 2

            y_ticks = np.arange(np.floor(y_min/y_step) * y_step, np.ceil(y_max/y_step) * y_step + y_step, y_step)
            ax.set_yticks(y_ticks)
            ax.yaxis.set_minor_locator(AutoMinorLocator(num_minor_ticks))

            ax.set_xticks(xticks)
            plt.xlabel('Receiver azimuth angle')
            plt.ylabel('Peak reflectivity [dB]')
            plt.grid()
            ax.xaxis.set_major_formatter(axis_formatter_degree)
            # plt.gca().xaxis.set_major_formatter(StrMethodFormatter("{x:}°"))

            # plt.title(f'Reflectivity Peak over Time for smap_sm: {smap_sm_group}, sc_alt: {sc_alt_group}, sp_inc_angle: {sp_inc_angle_group}')
            ax.set_position([0.18, 0.14, 0.75, 0.6])  # [left, bottom, width, height] in figure fraction
            legend_vbox = _get_fig_legend_bbox(n_rows)
            labels = [l.get_label() for l in lines]
            plt.legend(lines, labels, title='Soil moisture [$\mathrm{m}^3\mathrm{m}^{-3}$]', loc="upper center", bbox_to_anchor=(.5, legend_vbox), ncol=3,
                       fontsize=plt_font_size - (4 if plt_font_size > 16 else 0), handletextpad=0.0, borderpad=0.3, labelspacing=0.3,
                       columnspacing=0.3, markerscale=1.0)
            fig.set_figheight(_get_fig_height_from_leg_row(n_rows))  # Adjust the total figure height
            plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust rect to leave space for the legend

            img_name = img_tag + f'_peak_refl_vs_az_angle_varying_sm_inc_angle_{int(inc_angle):d}_alt_{alt_val}'
            save_figure(fig, folder_path, img_name, fig_save_types=fig_save_types)
            plt.close(fig)


def plot_reflectivity_vs_inc_angle_sm(grouped_data, folder_path, img_tag, fig_save_types):
    list_alt_vals = []
    list_az_angles = []
    for smap_sm_group, sc_alt_groups in grouped_data.items():
        for sc_alt_group, sp_inc_angle_groups in sc_alt_groups.items():
            if sc_alt_group not in list_alt_vals:
                list_alt_vals.append(sc_alt_group)
            for sp_inc_angle_group, sc_az_angle_groups in sp_inc_angle_groups.items():
                for az_angle_group in sc_az_angle_groups:
                    if az_angle_group not in list_az_angles:
                        list_az_angles.append(az_angle_group)

    for alt_val in list_alt_vals:
        for az_angle in list_az_angles:
            smap_sm_values = []
            sp_inc_angle_values = []
            reflectivity_peaks = []
            for smap_sm_group, sc_alt_groups in grouped_data.items():
                for sc_alt_group, sp_inc_angle_groups in sc_alt_groups.items():
                    for sp_inc_angle_group, sc_az_angle_groups in sp_inc_angle_groups.items():
                        for sc_az_angle_group, items in sc_az_angle_groups.items():
                            # Extract smap_sm, sp_inc_angle, and reflectivity_peak
                            smap_sm_values += [item['smap_sm'] for item in items if item['smap_sm'] > 0.0]
                            sp_inc_angle_values += [item['sp_inc_angle'] for item in items if item['smap_sm'] > 0.0]
                            reflectivity_peaks += [item['reflectivity_peak'] for item in items if item['smap_sm'] > 0.0]


            fig = plt.figure(figsize=(6, 4))
            ax = plt.subplot(111)
            # Create scatter plot
            reflectivity_peaks_db = lin2db(np.array(reflectivity_peaks))
            z_min = np.nanmin(reflectivity_peaks_db)
            z_max = np.nanmax(reflectivity_peaks_db)
            if (z_max - z_min) < 15.0:
                z_step = 2
                minor_tick_num = 2
            elif (z_max - z_min) < 30.0:
                z_step = 5
                minor_tick_num = 5
            else:
                z_step = 10
                minor_tick_num = 2

            _z_step = np.minimum(5, z_step)
            vmin = np.floor(z_min / _z_step) * _z_step
            vmax = np.ceil(z_max / _z_step) * _z_step
            scatter = plt.scatter(smap_sm_values, sp_inc_angle_values, c=reflectivity_peaks_db, cmap=sel_colormap,
                                  marker='o', vmin=vmin, vmax=vmax)
            cbar = plt.colorbar(scatter, label='Peak reflectivity [dB]')

            cbar_ticks = np.arange(vmin, vmax + z_step, z_step)
            cbar.set_ticks(cbar_ticks)
            cbar.ax.minorticks_on()
            cbar.ax.yaxis.set_minor_locator(AutoMinorLocator(minor_tick_num))  # For vertical colorbars

            ax.yaxis.set_major_formatter(axis_formatter_degree)
            plt.xlabel('Soil moisture $[\mathrm{m}^3 \mathrm{m}^{-3}]$')
            plt.xlim([0.0, 0.4])
            x_ticks = np.arange(0, 0.6, 0.1)
            ax.set_xticks(x_ticks)
            ax.xaxis.set_minor_locator(AutoMinorLocator(2))

            # Determine the tick range for y-axis

            y_ticks = np.arange(0, 70, 10)
            ax.set_yticks(y_ticks)
            ax.set_ylim([0, 65])
            ax.yaxis.set_minor_locator(AutoMinorLocator(2))

            plt.ylabel('$\\theta_\mathrm{i}$')
            plt.tight_layout()
            plt.tight_layout()
            plt.tight_layout()
            plt.tight_layout()
            plt.tight_layout()
            az_ang_str = 'n' if az_angle < 0 else ''
            az_ang_str += str(abs(int(az_angle)))
            img_name = img_tag + f'_peak_refl_vs_sm_inc_angle_alt_{alt_val}_az_{az_ang_str}'
            save_figure(fig, folder_path, img_name, fig_save_types=fig_save_types)
            plt.close(fig)



def plot_reflectivity_vs_inc_angle_sm_all_az(grouped_data, folder_path, img_tag, fig_save_types):
    list_alt_vals = []
    list_az_angles = []
    for smap_sm_group, sc_alt_groups in grouped_data.items():
        for sc_alt_group, sp_inc_angle_groups in sc_alt_groups.items():
            if sc_alt_group not in list_alt_vals:
                list_alt_vals.append(sc_alt_group)
            for sp_inc_angle_group, sc_az_angle_groups in sp_inc_angle_groups.items():
                for az_angle_group in sc_az_angle_groups:
                    if az_angle_group not in list_az_angles:
                        list_az_angles.append(az_angle_group)

    for alt_val in list_alt_vals:
        smap_sm_values = []
        sp_inc_angle_values = []
        reflectivity_peaks = []

        for az_angle in list_az_angles:
            for smap_sm_group, sc_alt_groups in grouped_data.items():
                for sc_alt_group, sp_inc_angle_groups in sc_alt_groups.items():
                    for sp_inc_angle_group, sc_az_angle_groups in sp_inc_angle_groups.items():
                        for sc_az_angle_group, items in sc_az_angle_groups.items():
                            # Extract smap_sm, sp_inc_angle, and reflectivity_peak
                            smap_sm_values += [item['smap_sm'] for item in items if item['smap_sm'] > 0.0]
                            sp_inc_angle_values += [item['sp_inc_angle'] for item in items if item['smap_sm'] > 0.0]
                            reflectivity_peaks += [item['reflectivity_peak'] for item in items if item['smap_sm'] > 0.0]


        fig = plt.figure(figsize=(6, 4))
        ax = plt.subplot(111)
        # Create scatter plot
        reflectivity_peaks_db = lin2db(np.array(reflectivity_peaks))
        max_dynamic_range = 20
        z_min = np.nanmin(reflectivity_peaks_db)
        z_max = np.nanmax(reflectivity_peaks_db)
        if (z_max - z_min) < 15.0:
            z_step = 2
            minor_tick_num = 2
        elif (z_max - z_min) < 30.0:
            z_step = 5
            minor_tick_num = 5
        else:
            z_step = 5
            minor_tick_num = 2
        _z_step = np.minimum(5, z_step)
        vmin = np.floor(z_min / _z_step) * _z_step
        vmax = np.ceil(z_max / _z_step) * _z_step

        if (vmax - vmin) > max_dynamic_range:  # restrict dynamic range
            z_median = np.nanmedian(reflectivity_peaks_db)
            z_mid = np.floor(z_median / _z_step) * _z_step
            vmin = z_mid - max_dynamic_range/2
            vmax = z_mid + max_dynamic_range/2

        scatter = plt.scatter(smap_sm_values, sp_inc_angle_values, c=reflectivity_peaks_db, cmap=sel_colormap, marker='o', vmin=vmin, vmax=vmax)
        cbar = plt.colorbar(scatter, label='Peak reflectivity [dB]')

        cbar_ticks = np.arange(vmin, vmax + z_step, z_step)
        cbar.set_ticks(cbar_ticks)
        cbar.ax.minorticks_on()
        cbar.ax.yaxis.set_minor_locator(AutoMinorLocator(minor_tick_num))  # For vertical colorbars

        ax.yaxis.set_major_formatter(axis_formatter_degree)

        plt.xlabel('Soil moisture $[\mathrm{m}^3 \mathrm{m}^{-3}]$')
        plt.xlim([0.0, 0.4])
        x_ticks = np.arange(0, 0.6, 0.1)
        ax.set_xticks(x_ticks)
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))

        # Determine the tick range for y-axis
        y_ticks = np.arange(0, 70, 10)
        ax.set_yticks(y_ticks)
        ax.set_ylim([0, 65])
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))

        plt.ylabel('$\\theta_\mathrm{i}$')
        plt.tight_layout()
        plt.tight_layout()
        img_name = img_tag + f'_peak_refl_vs_sm_inc_angle_alt_{alt_val}_all_az'
        save_figure(fig, folder_path, img_name, fig_save_types=fig_save_types)
        plt.close(fig)


def save_figure(fig, fig_out_folder, img_save_name, tf_save_fig=True, fig_save_types: Optional[list[str]] = None):
    """
    save figure

    :param fig: figure object
    :param fig_out_folder: image saving folder
    :param img_save_name: image save name
    :param tf_save_fig: save the figure?
    :param fig_save_types: type of image? png, eps, pdf, svg ...
    :return: True if image is saved, else False
    """
    if not tf_save_fig:
        return False
    if fig_save_types is None:
        fig_save_types = default_save_type
    elif type(fig_save_types) is str:
        fig_save_types = [fig_save_types]
    for fig_type in fig_save_types:
        name = f"{img_save_name.split('.')[0]}.{fig_type}"
        fig.savefig(os.path.join(fig_out_folder, name), format=fig_type, bbox_inches='tight')
    return True