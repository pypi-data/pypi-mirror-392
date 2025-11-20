import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
from sklearn.cross_decomposition import PLSRegression
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt
from nml.model_interactor import ModelInteractor

filename = "C:/MyRepos/Python/mindrove/data/max_2024_11_07_4_emg_xy.csv"
# Load the CSV file
M = pd.read_csv(filename)

# Generate time column based on sample rate (assuming first time point is start time)
sample_rate = 500  # Hz
M['time'] = pd.to_datetime(M['time'][0]) + pd.to_timedelta(np.arange(len(M)) / sample_rate, unit='s')

# Wrap angle to 360 degrees
M['angle'] = np.rad2deg(M['angle']) % 360

# Define a lowpass filter for the EMG envelope (cutoff 8 Hz)
b, a = butter(3, 8 / (sample_rate / 2), btype='low')
for ii in range(1, 9):
    hpf_emg = M[f"feature_{ii}"]
    env_emg = filtfilt(b, a, np.abs(hpf_emg))
    M[f"envelope_{ii}"] = env_emg

# Define a lowpass filter for x, y, and angle (cutoff 10 Hz)
b, a = butter(3, 10 / (sample_rate / 2), btype='low')
M['angle'] = filtfilt(b, a, M['angle'])
M['x'] = filtfilt(b, a, M['x'])
M['y'] = filtfilt(b, a, M['y'])

# Calculate dx and dy as filtered gradients of x and y, respectively
b, a = butter(3, 2.5 / (sample_rate / 2), btype='low')
M['dx'] = filtfilt(b, a, np.gradient(M['x']))
M['dy'] = filtfilt(b, a, np.gradient(M['y']))

# Process the button data if it exists
if 'button_1' in M.columns:
    M['edge_1'] = np.zeros(len(M))
    button_1 = M['button_1'].values
    rising_samples = np.where((button_1[:-1] == 0) & (button_1[1:] == 1))[0]
    falling_samples = np.where((button_1[:-1] == 1) & (button_1[1:] == 0))[0]

    # Define helper function to get indices around transitions
    def get_transition_indices(samples, n_samples, offsets=[-15, -5, 5, 15]):
        copies = [np.clip(samples + offset, 0, n_samples - 1) for offset in offsets]
        return np.unique(np.concatenate(copies))

    rising_copies = get_transition_indices(rising_samples, len(M))
    falling_copies = get_transition_indices(falling_samples, len(M))

    # Set edges based on transitions
    M['edge_1'].iloc[rising_copies] = 1
    M['edge_1'].iloc[falling_copies] = -1

    # Convolve with a window (assuming options.EdgeTransitionWindowSamples is defined)
    window_samples = 5  # Example value; replace with options.EdgeTransitionWindowSamples if available
    M['edge_1'] = np.convolve(M['edge_1'], np.ones(window_samples), mode='same')

# 2. Preprocess data for state and control variables
# Assuming columns in 'data' similar to MATLAB structure
# `M.dx`, `M.dy` represent states, and columns 23 to 16 as control data
state_data = np.column_stack((M['dx'], M['dy'] * 1.5))
control_data = M.iloc[:, 22:14:-1].to_numpy()

# 3. Apply PLS regression
pls = PLSRegression(n_components=6)
pls.fit(control_data, state_data)

beta_pls = np.vstack((pls.intercept_.T, pls.coef_.T))

# 4. Predict the state estimates
state_estimate = control_data @ pls.coef_.T + pls.intercept_.T
# state_estimate = pls.predict(control_data) # equivalent

# 5. Prepare timestamps
# Ensure date and time are strings before concatenating
timestamps = M['time']
dt = (timestamps[1] - timestamps[0]).total_seconds()  # Sampling interval

# 6. Plot results
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].plot(timestamps, state_data[:, 0] / dt, label="Measured", color="k")
axes[0].plot(timestamps, state_estimate[:, 0] / dt, label="Estimated", color="b", linestyle=":")
axes[0].set_title("Horizontal Angular Velocity")
axes[0].set_xlabel("Time")
axes[0].set_ylabel("Angular Velocity (°/s)")

axes[1].plot(timestamps, state_data[:, 1] / (1.5 * dt), label="Measured", color="k")
axes[1].plot(timestamps, state_estimate[:, 1] / (1.5 * dt), label="Estimated", color="b", linestyle=":")
axes[1].set_title("Vertical Angular Velocity")
axes[1].set_xlabel("Time")
axes[1].set_ylabel("Angular Velocity (°/s)")

plt.legend()
plt.tight_layout()
plt.show()

ModelInteractor.print_model(beta_pls)