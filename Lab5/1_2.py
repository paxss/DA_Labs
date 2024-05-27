import matplotlib.pyplot as plt
from matplotlib.widgets import Button, CheckButtons, Slider

import numpy as np
from scipy import signal

AMPLITUDE = 1.0
FREQUENCY = 1.0
PHASE = 0.0
NOISE_MEAN = 0.0
NOISE_DISPERSION = 0.1
SHOW_NOISE = True
NOISE = np.random.normal(0, 1, 1000)

def harmonic_with_noise(amplitude, frequency, phase, noise_mean, noise_coveriance, show_noise=True):
    t = np.linspace(0, 10, 1000)
    y = amplitude * np.sin(2 * np.pi * frequency * t + phase)

    if show_noise:
        scaled_noise = noise_mean + np.sqrt(noise_coveriance) * NOISE
        y += scaled_noise

    return t, y

def filter_signal(y, cutoff_frequency=0.03, order=4):
    b, a = signal.butter(order, cutoff_frequency, btype='low', analog=False)
    f_y = signal.filtfilt(b, a, y)
    return f_y

def update(event):
    AMPLITUDE = amplitude_slider.val
    FREQUENCY = frequency_slider.val
    PHASE = phase_slider.val
    NOISE_MEAN = noise_mean_slider.val
    NOISE_DISPERSION = noise_dispersion_slider.val

    cutoff_frequency = cutoff_slider.val
    order = order_slider.val

    SHOW_NOISE = show_noise_chbx.get_status()[0]

    t, y = harmonic_with_noise(AMPLITUDE, FREQUENCY, PHASE, NOISE_MEAN, NOISE_DISPERSION, SHOW_NOISE)
    f_y = filter_signal(y, cutoff_frequency, order)

    line1.set_data(t, y)
    line2.set_data(t, f_y)

    fig.canvas.draw_idle()

def reset(event):
    amplitude_slider.reset()
    frequency_slider.reset()
    phase_slider.reset()
    noise_mean_slider.reset()
    noise_dispersion_slider.reset()
    update(None)

def create_new_noise(event):
    global NOISE
    NOISE = np.random.normal(0, 1, 1000)
    update(None)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 9), gridspec_kw={'height_ratios': [1.5, 1.5]})
fig.canvas.manager.set_window_title('Лабораторна робота 5(1-2)')
plt.subplots_adjust(bottom=0.5, hspace=0.9)

t, y = harmonic_with_noise(AMPLITUDE, FREQUENCY, PHASE, NOISE_MEAN, NOISE_DISPERSION, SHOW_NOISE)
f_y = filter_signal(y)

line1, = ax1.plot(t, y, lw=2, color='b', label='Original Signal')
line2, = ax2.plot(t, f_y, lw=2, color='g', label='Filtered Signal')

ax1.set_xlabel('Час')
ax1.set_ylabel('Амплітуда')
ax1.set_title('З шумом')
ax1.set_ylim(-2, 2)

ax2.set_xlabel('Час')
ax2.set_ylabel('Амплітуда')
ax2.set_title('Відфільтрована')
ax2.set_ylim(-2, 2)

amplitude_slider = Slider(plt.axes([0.1, 0.4, 0.80, 0.03]), 'Amplitude', 0.1, 5.0, valinit=AMPLITUDE, valstep=0.05)
amplitude_slider.on_changed(update)

frequency_slider = Slider(plt.axes([0.1, 0.35, 0.80, 0.03]), 'Frequency', 0.1, 5.0, valinit=FREQUENCY, valstep=0.005)
frequency_slider.on_changed(update)

phase_slider = Slider(plt.axes([0.1, 0.3, 0.80, 0.03]), 'Phase', -np.pi, np.pi, valinit=PHASE, valstep=0.1)
phase_slider.on_changed(update)

noise_mean_slider = Slider(plt.axes([0.1, 0.25, 0.80, 0.03]), 'Mean', -1.0, 1.0, valinit=NOISE_MEAN, valstep=0.01)
noise_mean_slider.on_changed(update)

noise_dispersion_slider = Slider(plt.axes([0.1, 0.2, 0.80, 0.03]), 'Dispersion', 0.00, 1.0, valinit=NOISE_DISPERSION, valstep=0.01)
noise_dispersion_slider.on_changed(update)



cutoff_slider = Slider(plt.axes([0.1, 0.1, 0.50, 0.03]), 'Cutoff', 0.01, 0.99, valinit=0.03, valstep=0.01)
cutoff_slider.on_changed(update)

order_slider = Slider(plt.axes([0.1, 0.05, 0.50, 0.03]), 'Order', 1.0, 20.0, valinit=4, valstep=1)
order_slider.on_changed(update)


show_noise_chbx = CheckButtons(plt.axes([0.65, 0.09, 0.33, 0.03]), ['Показувати шум'], [SHOW_NOISE])
show_noise_chbx.on_clicked(update)

reset_btn = Button(plt.axes([0.65, 0.058, 0.16, 0.03]), 'Reset')
reset_btn.on_clicked(reset)

new_noise_btn = Button(plt.axes([0.82, 0.058, 0.16, 0.03]), 'New Noise')
new_noise_btn.on_clicked(create_new_noise)

plt.show()