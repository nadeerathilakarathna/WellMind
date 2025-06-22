import matplotlib.pyplot as plt
import numpy as np
import time

def live_plot(stress_data):
    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot([], [], '-o')
    ax.set_ylim(0, 1)
    ax.set_xlim(0, 100)
    ax.set_title("Live Stress Level")
    ax.set_xlabel("Time Frame")
    ax.set_ylabel("Stress Probability")

    while True:
        data = list(stress_data)[-100:]  # last 100 values
        if data:
            y_data = np.array(data)
            x_data = np.arange(len(y_data))

            line.set_xdata(x_data)
            line.set_ydata(y_data)
            ax.set_xlim(0, max(10, len(x_data)))

            fig.canvas.draw()
            fig.canvas.flush_events()
        time.sleep(1)


def live_plot_multiple_models(stress_data1,stress_data2, stress_data3, stress_data4):
    plt.ion()
    fig, ax = plt.subplots()

    # Initialize 4 lines with different colors and labels
    line1, = ax.plot([], [], '-', label='Model 1', color='cyan')
    line2, = ax.plot([], [], '-', label='Model 2', color='blue')
    line3, = ax.plot([], [], '-', label='Model 3', color = 'green')
    line4, = ax.plot([], [], '-', label='Model 4', color = 'black')

    ax.set_ylim(0, 1)
    ax.set_xlim(0, 100)
    ax.set_title("Live Stress Level Comparison")
    ax.set_xlabel("Time Frame")
    ax.set_ylabel("Stress Probability")
    ax.legend()

    while True:
        # Take last 100 from each data list
        data1 = list(stress_data1)[-100:]
        data2 = list(stress_data2)[-100:]
        data3 = list(stress_data3)[-100:]
        data4 = list(stress_data4)[-100:]

        x1 = np.arange(len(data1))
        x2 = np.arange(len(data2))
        x3 = np.arange(len(data3))
        x4 = np.arange(len(data4))

        # Update each line
        line1.set_xdata(x1)
        line1.set_ydata(data1)

        line2.set_xdata(x2)
        line2.set_ydata(data2)

        line3.set_xdata(x3)
        line3.set_ydata(data3)

        line4.set_xdata(x4)
        line4.set_ydata(data4)

        # Dynamically adjust x-axis
        ax.set_xlim(0, max(100, len(data1), len(data2), len(data3), len(data4)))

        fig.canvas.draw()
        fig.canvas.flush_events()
        time.sleep(1)