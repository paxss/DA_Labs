import subprocess

from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row, gridplot
from bokeh.palettes import Plasma256 as palette
from bokeh.models import Button, CheckboxGroup, Select, Slider

import numpy as np

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

def median_filter(y, window_size):
    f_y = np.zeros_like(y)
    padding = window_size // 2

    for i in range(len(y)):
        window = np.zeros(window_size)
        for j in range(window_size):
            index = i + j - padding
            if index < 0:
                index = 0
            elif index >= len(y):
                index = len(y) - 1
            window[j] = y[index]
        f_y[i] = np.median(window)

    return f_y

def exponential_filter(y, alpha):
    f_y = np.zeros_like(y)
    f_y[0] = y[0]
    
    for i in range(1, len(y)):
        f_y[i] = alpha * y[i] + (1 - alpha) * f_y[i-1]
        
    return f_y

def create_new_noise(event):
    global NOISE
    NOISE = np.random.normal(0, 1, 1000)
    update(None, None, None)

def update(attr, old, new):
    
    amplitude = amplitude_slider.value
    frequency = frequency_slider.value
    phase = phase_slider.value
    noise_mean = mean_slider.value
    noise_dispersion = dispersion_slider.value

    bool_noise = 0 in show_noise.active

    t, y = harmonic_with_noise(amplitude, frequency, phase, noise_mean, noise_dispersion, bool_noise)

    first_line.data_source.data = {"x": t, "y": y}

    if filter_selector.value == "exp":
        f_y = exponential_filter(y, alpha_slider.value)

    else:
        f_y = median_filter(y, window_slider.value)

    second_line.data_source.data = {"x": t, "y": f_y}

def reset():
    amplitude_slider.value = AMPLITUDE
    frequency_slider.value = FREQUENCY
    phase_slider.value = PHASE
    mean_slider.value = NOISE_MEAN
    dispersion_slider.value = NOISE_DISPERSION

    alpha_slider.value = 0.6
    window_slider.value = 1

first_plot = figure(title="Оригінал", x_axis_label='Час', y_axis_label='Амплітуда', x_axis_type="linear", y_axis_type="linear", background_fill_color="#F0F0F0")
first_plot.width = 400
first_plot.height = 400
first_line = first_plot.line([], [], line_width=3, line_color=palette[80], line_cap="round", line_join="round")

second_plot = figure(title="Відфільтровано", x_axis_label='Час', y_axis_label='Амплітуда', x_axis_type="linear", y_axis_type="linear", background_fill_color="#F0F0F0")
second_plot.width = 400
second_plot.height = 400
second_line = second_plot.line([], [], line_width=3, line_color=palette[80], line_cap="round", line_join="round")

slider_config = {"width": 200, "bar_color": palette[100]}

amplitude_slider = Slider(title="Amplitude", value=AMPLITUDE, start=0.1, end=5.0, step=0.1, **slider_config)
frequency_slider = Slider(title="Frequency", value=FREQUENCY, start=0.1, end=5.0, step=0.1, **slider_config)
phase_slider = Slider(title="Phase", value=PHASE, start=-np.pi, end=np.pi, step=0.1, **slider_config)
mean_slider = Slider(title="Mean", value=NOISE_MEAN, start=-1.0, end=1.0, step=0.1, **slider_config)
dispersion_slider = Slider(title="Dispersion", value=NOISE_DISPERSION, start=0.01, end=1.0, step=0.01, **slider_config)

alpha_slider = Slider(title="Alpha", value=0.6, start=0.01, end=0.9, step=0.01, **slider_config)
window_slider = Slider(title="Window", value=1, start=1, end=50, step=1, **slider_config)

show_noise = CheckboxGroup(labels=["Показувати шум"], active=[0], width=200)
filter_selector = Select(title="Фільтр", value="exp", options = ["exp", "med"], width=200)

reset_btn = Button(label="Reset", button_type="success", width=200)
new_noise_btn = Button(label="Новий шум", button_type="warning", width=200)

amplitude_slider.on_change("value", update)
frequency_slider.on_change("value", update)
phase_slider.on_change("value", update)
mean_slider.on_change("value", update)
dispersion_slider.on_change("value", update)

show_noise.on_change("active", update)
filter_selector.on_change("value", update)

alpha_slider.on_change("value", update)
window_slider.on_change("value", update)

reset_btn.on_click(reset)
new_noise_btn.on_click(create_new_noise)

update(None, None, None)

layout = column(
    row(first_plot, second_plot),
    row(
        column(amplitude_slider, frequency_slider, phase_slider, mean_slider, dispersion_slider),
        column(alpha_slider, window_slider),
        column(show_noise, filter_selector, reset_btn, new_noise_btn)
    )
    
)
curdoc().add_root(layout)

if __name__ == "__main__":
    subprocess.run(["bokeh", "serve", "--show", __file__])