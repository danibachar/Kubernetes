import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
import numpy as np
from datetime import datetime

from scipy import signal

matplotlib.rcParams['agg.path.chunksize'] = 10000

X_AXIS = 'timeStamp'
Y_AXIS_1 = 'elapsed'
Y_AXIS_2 = 'success'
Y_AXIS_3 = 'Latency'
Y_AXIS_4 = 'Connect'


# Data for plotting
df = pd.read_csv('./test.csv')

# Simple axis plot
def time_transform(timestamp):
    return datetime.fromtimestamp(float(timestamp)/1000)


def plot_ticks():
    y = list(df[Y_AXIS_1])
    fig, ax = plt.subplots()
    ax.plot(y, linewidth=0.2, markersize=1)
    return ax

def plot_time():
    x = list(map(time_transform, df[X_AXIS]))
    y = list(df[Y_AXIS_1])
    fig, ax = plt.subplots()

    ax.plot(x, y)

    return ax

def plot_with_grid():
    y = list(df[Y_AXIS_1])
    x = np.arange(len(y))
    fig, ax = plt.subplots()

    major_ticks = np.arange(0, 101, 20)
    minor_ticks = np.arange(0, 101, 5)

    ax.set_xticks(major_ticks)
    ax.set_xticks(minor_ticks, minor=True)
    ax.set_yticks(major_ticks)
    ax.set_yticks(minor_ticks, minor=True)

    # And a corresponding grid
    ax.grid(which='both')

    # Or if you want different settings for the grids:
    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)

    ax.plot(x, y)

    return ax

def plt_combine():
    y1 = df[Y_AXIS_1]
    y2 = df[Y_AXIS_2]
    y3 = df[Y_AXIS_3]

    x = np.arange(len(y1))


    fig, ax = plt.subplots()

    # Original Plotting
    plt.yscale('log')
    ax.plot(x, y1, "b-", linewidth=1)
    ax.plot(x, y3, "g-", linewidth=0.2)

    y1 = signal.savgol_filter(
        y1,
        int(np.percentile(y1,95)),  # window size used for filtering
        4
    )

    # Smooth Plotting
    # plt.yscale('linear')
    ax.plot(x, y1, "r-", linewidth=1)


    # y2 = signal.savgol_filter(
    #     y2,
    #     int(np.percentile(y2,95)),  # window size used for filtering
    #     3
    # )
    #
    # y3 = signal.savgol_filter(
    #     y3,
    #     int(np.percentile(y3, 95)),  # window size used for filtering
    #     3
    # )





    # ax.plot(x, y3, "g-", linewidth=1.5)
    # ax.scatter(x, y2, c=(y2 != True).astype(float))
    return ax

# fig.savefig("test.png")
# beautify the x-labels
ax = plt_combine()

ax.set(
        xlabel='time (date)',
        ylabel='request total time (ms)',
        title='attack'
)

plt.gcf().autofmt_xdate()

plt.show()


# plt.gca().xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S.%f"))