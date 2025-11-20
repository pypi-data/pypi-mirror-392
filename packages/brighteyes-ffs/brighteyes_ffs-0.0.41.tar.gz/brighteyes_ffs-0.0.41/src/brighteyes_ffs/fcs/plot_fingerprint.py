import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
import numpy as np
from .distance2detelements import distance2detelements
from ..tools.cast_data import cast_data
from ..tools.color_from_map import color_from_map


def plot_fingerprint_airyscan(counts, cmap='inferno', plot=False):
    """
    Plot the airyscan fingerprint from a data set with the photon counts for
    each of the 32 detector elements.
    The elements in counts are plotted in the following way:
    
            22  21
      23  10  9   8  20
    24  11  2   1   7  19
      12  3   0   6  18  31
    25  13  4   5  17  30
      26 14  15  16  29
           27  28

    Parameters
    ----------
    counts : np.array
        Array with the 32 photon counts of the airyscan.
        Channel numbers according to Zeiss (ch 0 = center)
    plot : boolean, optional
        Plot the finger print

    Returns
    -------
    sx, sy : list
        x and y coordinates of the hexagons
    c : np.array()
        2D array with RGBA values for each hexagon

    """
    
    n_elements= 32
    
    shiftx = np.cos(30*np.pi/180)
    sx = np.zeros((n_elements,2))
    sx[0] = [0,0]

    sx[1] = [shiftx,1.5]
    sx[2] = [-shiftx,1.5]
    sx[3] = [-2*shiftx,0]
    sx[4] = [-shiftx,-1.5]
    sx[5] = [shiftx,-1.5]
    sx[6] = [2*shiftx,0]

    sx[7] = [3*shiftx,1.5]
    sx[8] = [2*shiftx,3]
    sx[9] = [0,3]
    sx[10] = [-2*shiftx,3]
    sx[11] = [-3*shiftx,1.5]
    sx[12] = [-4*shiftx,0]
    sx[13] = [-3*shiftx,-1.5]
    sx[14] = [-2*shiftx,-3]
    sx[15] = [0,-3]
    sx[16] = [2*shiftx,-3]
    sx[17] = [3*shiftx,-1.5]
    sx[18] = [4*shiftx,0]

    sx[19] = [5*shiftx,1.5]
    sx[20] = [4*shiftx,3]
    sx[21] = [shiftx,4.5]
    sx[22] = [-shiftx,4.5]
    sx[23] = [-4*shiftx,3]
    sx[24] = [-5*shiftx,1.5]
    sx[25] = [-5*shiftx,-1.5]
    sx[26] = [-4*shiftx,-3]
    sx[27] = [-shiftx,-4.5]
    sx[28] = [shiftx,-4.5]
    sx[29] = [4*shiftx,-3]
    sx[30] = [5*shiftx,-1.5]
    sx[31] = [6*shiftx,0]
    
    cmin = np.min(counts)
    cmax = np.max(counts)
    color_code = np.zeros((n_elements, 3))
    
    for i in range(n_elements):
        color_code[i,:] = color_from_map(counts[i], startv=cmin, stopv=cmax, cmap=cmap)
    
    if plot:
        plt.figure()
        ax = plt.subplot(1,1,1)
        for x, y, c in zip(sx[:,0], sx[:,1], color_code):
            color = c
            ax.add_patch(RegularPolygon((x, y),
                                        numVertices=6,
                                        radius=1.0, 
                                        orientation=np.radians(120),
                                        facecolor = color,
                                        alpha=1))
        
        plt.xlim([-6,6])
        plt.ylim([-6,6])
        plt.xticks([])
        plt.yticks([])
        ax.set_axis_off()
        ax.set_box_aspect(1)
    
    return list(sx[:,0]), list(sx[:,1]), color_code


def plot_fingerprint_luminosa(counts, cmap='inferno', plot=False):
    """
    Plot the airyscan fingerprint from a data set with the photon counts for
    each of the 23 detector elements

    Parameters
    ----------
    counts : np.array
        1D array with the 23 photon counts of the airyscan.
        Channel numbers according to Zeiss (ch 0 = center)
    plot : boolean, optional
        Plot the finger print

    Returns
    -------
    hexb : np.array()
        Array for hexbin plotting

    """
    
    n_elements= 23
    
    cmin = np.min(counts)
    cmax = np.max(counts)
    color_code = np.zeros((n_elements, 3))
    
    for i in range(n_elements):
        color_code[i,:] = color_from_map(counts[i], startv=cmin, stopv=cmax, cmap=cmap)
    
    sx  = [4.0, 2.0, 0.0, -2.0, -4.0, 3.0, 1.0, -1.0, -3.0, 4.0, 2.0, 0.0, -2.0, -4.0, 3.0, 1.0, -1.0, -3.0, 4.0, 2.0, 0.0, -2.0, -4.0]
    sy = [-3.46, -3.46, -3.46, -3.46, -3.46, -1.73, -1.73, -1.73, -1.73, 0.0, 0.0, 0.0, 0.0, 0.0, 1.73, 1.73, 1.73, 1.73, 3.46, 3.46, 3.46, 3.46, 3.46]
    
    # make a plot of the detector array
    if plot:
        plt.figure()
        ax = plt.subplot(1,1,1)
        # Add some coloured hexagons
        for x, y, c in zip(sx, sy, color_code):
            color = c
            ax.add_patch(RegularPolygon((x, y),
                                        numVertices=6,
                                        radius=1.15, 
                                        orientation=np.radians(120),
                                        facecolor = color,
                                        alpha=1))
        plt.xlim((-5,5))
        plt.ylim((-4.6,4.6))
        ax.set_box_aspect(1)
        ax.set_axis_off()
    
    return sx, sy, color_code


def plot_fingerprint5x5(data, show_perc=True, dtype='int64', normalize=False, savefig=0, vminmax = 'auto'):
    """
    Make finger print plot of SPAD-fcs data with 25 channels.

    Parameters
    ----------
    data : np.array()
        Nx26 or Nx25 array with the fcs data
        or data object with data.det0 etc. arrival times.
    show_perc : boolean, optional
        Show percentages. The default is True.
    dtype : string, optional
        Data type. The default is 'int64'.
    normalize : boolean, optional
        Convert total counts to average counts per bin if True. The default is False.
    savefig : int, optional
        Path to store figure. The default is 0.
    vminmax : vector or string, optional
        Vector with minimum and maximum color bar value. The default is 'auto'.

    Returns
    -------
    airy : np.array()
        26 element vector with the sum of the rows and plot.

    """
    
    if type(data) == np.ndarray:
        # data is numpy array with intensity traces
        if len(np.shape(data)) > 1:
            # if 2D array, convert to dtype and sum over all rows
            data = cast_data(data, dtype)
            airy = np.sum(data, axis=0)
        else:
            airy = data
        airy2 = airy[0:25]
    else:
        if hasattr(data, 'det24'):
            # data is fcs2arrivaltimes.ATimesData object with 25 elements
            airy2 = np.zeros(25)
            for det in range(25):
                airy2[det] = len(getattr(data, 'det' + str(det)))
        else:
            # data is fcs2arrivaltimes.ATimesData object with 21 elements
            airy2 = np.zeros(25)
            # *  0  1  2  *
            # 3  4  5  6  7
            # 8  9  10 11 12
            # 13 14 15 16 17
            # *  18 19 20 *
            dets = [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23]
            for det in range(21):
                if hasattr(data, 'det' + str(det)):
                    airy2[dets[det]] = len(getattr(data, 'det' + str(det)))
                else:
                    airy2[dets[det]] = 0
        airy = airy2
    
    if normalize:
        airy2 = airy2 / np.size(data, 0)
    
    airyMax = np.max(airy2)
    airyMin = np.min(airy2)
    airyCentPerc = (0.2 * (airyMax - airyMin) + airyMin) / airyMax * 100
        
    airy2 = airy2.reshape(5, 5)
    
    
    plt.figure()
    fontSize = 20
    plt.rcParams.update({'font.size': fontSize})
    plt.rcParams['mathtext.rm'] = 'Arial'
    
    if vminmax == 'auto':
        plt.imshow(airy2, cmap='hot', interpolation='nearest')
    else:
        plt.imshow(airy2, cmap='hot', interpolation='nearest', vmin=vminmax[0], vmax=vminmax[1])
    ax = plt.gca()
    
    # Major ticks
    ax.set_xticks([])
    ax.set_yticks([])
    # Labels for major ticks
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    # Minor ticks
    ax.set_xticks(np.arange(-0.5, 4.5, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, 5.5, 1), minor=True)
    # Gridlines based on minor ticks
    #ax.grid(which='minor', color='w', linestyle='-', linewidth=1)
    ax.tick_params(axis=u'both', which=u'both',length=0)
    
    cbar = plt.colorbar()
    cbar.ax.tick_params(labelsize=fontSize)

    if type(show_perc) is str and show_perc=="numbers":
        for i in range(5):
            for j in range(5):
                if vminmax == 'auto':
                    perc = round(airy2[i, j] / airyMax * 100)
                else:
                    perc = round(airy2[i, j] / vminmax[1] * 100)
                c="k"
                if perc < airyCentPerc:
                    c="w"
                plt.text(j, i, '{:.1f}'.format(airy2[i, j]), ha="center", va="center", color=c, fontsize=18)    
    elif show_perc:
        for i in range(5):
            for j in range(5):
                if vminmax == 'auto':
                    perc = round(airy2[i, j] / airyMax * 100)
                else:
                    perc = round(airy2[i, j] / vminmax[1] * 100)
                c="k"
                if perc < airyCentPerc:
                    c="w"
                plt.text(j, i, '{:.0f}%'.format(perc), ha="center", va="center", color=c, fontsize=18)

    if savefig != 0:
        plt.tight_layout()
        if savefig[-3:] == 'svg':
            plt.rcParams['svg.fonttype'] = 'none'
        plt.savefig(savefig, format=savefig[-3:])

    return airy

def plot_det_dist():
    det = []
    for i in range(25):
        det.append(distance2detelements(i, 12))
    det = np.resize(det, (5, 5))
    plt.figure()
    plt.imshow(det, cmap='viridis')