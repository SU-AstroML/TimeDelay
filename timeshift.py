import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import correlate, detrend
from timedelay.correlation import *
from scipy import signal
import sys

def timeshift_mse(x1, x2):
    res = np.zeros(len(x1) * 2 - 1)
    xlen = len(x1)
    off = xlen / 2
    for i in xrange(-xlen+1, xlen):
        left = max(0, -i)
        right = max(0, i)
        xr = x1[left:xlen-right] - x2[right:xlen-left]
        res[i] = np.sum(xr**2) / len(xr)
    return res


def timeshift_correlate(sig1, sig2):
    return signal.correlate(sig1, sig2, mode="full")

def timeshift(data, correlator, dt = 0.1):
    output = None
    windows = np.unique(data['window_id'])
    for i, window in enumerate(windows):
        print "Window %s" % window
        t = data['t_eval'][data['window_id']==window]
        t = t - np.min(t)
        sigA = data['sig_evalA'][data['window_id']==window]
        #    sigA = detrend(sigA)
        sigA = (sigA - np.mean(sigA)) / np.std(sigA)

        sigB = data['sig_evalB'][data['window_id']==window]
        #    sigB = detrend(sigB)
        sigB = (sigB - np.mean(sigB)) / np.std(sigB)

        corr = correlator(sigA, sigB)

        res = np.zeros(len(corr), dtype=[('pair_id', 'f4'), ('window_id', 'f4'), ('offset', 'f4'), ('correlation', 'f4'), ('dt', '<f4'), ('tau', '<f4'), ('sig', '<f4'), ('m1', '<f4'), ('m2', '<f4')])

        res['window_id'] = window
        for name in ('pair_id', 'dt', 'tau', 'sig', 'm1', 'm2'):
            res[name] = data[name][data['window_id']==window][0]

        res['offset'] = dt * np.arange(-len(sigA)+1, len(sigA), 1)
        res['correlation'] = corr

        if output is None:
            output = res
        else:
            output = np.append(output, res)
    return output

data = np.load("TimeDelayData/gp_resampled_of_windows_with_truth.npz")['arr_0']
if sys.argv[1] == 'mse':
    data = timeshift(data, timeshift_mse)
elif sys.argv[1] == 'correlate':
    data = timeshift(data, timeshift_correlate)
else:
    raise Exception("Unknown correlation mode")

np.savez(sys.argv[2], data)
