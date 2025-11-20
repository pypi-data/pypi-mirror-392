import numpy as np
from mindrove.board_shim import BoardShim
from numpy.typing import NDArray
from scipy.signal import butter, sosfilt, sosfilt_zi
from nml.binary_logger import BinaryLogger
from nml.binary_reader import BinaryReader
from nml.model_interactor import ModelInteractor
from nml.cluster_selection_window import ClusterSelectionWindow
from nml.spikes import BeamformerSpikeHandler
from nml.connections.parameter_socket import ParameterSocket
from nml.connections.stream_socket import StreamSocket
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QTimer
from typing import Tuple
from nml.feature_weights import model
from nml.processor_modes import ProcessorMode
from nml.decoder import Decoder

class Processor(QObject):
    board_shim: BoardShim | None = None
    spike = pyqtSignal(object, int, int)
    motor_units = pyqtSignal(object)
    cluster_color_assigned = pyqtSignal(int, QColor)
    auto_thresholds = pyqtSignal(object)
    omega = pyqtSignal(object, object, object, object, bool)
    delta_omega = pyqtSignal(float, float, float, float)
    embedding = pyqtSignal(float, float, int, int, float, int)

    parameter_socket: ParameterSocket | None = None
    stream_socket: StreamSocket | None = None
    
    _decoder: Decoder | None = None
    _decode_mode: ProcessorMode = ProcessorMode.ANGULAR_VELOCITY
    @property
    def decode_mode(self) -> ProcessorMode:
        return self._decode_mode

    circular_buffer: "np.ndarray[np.float64]"  = None # pyright: ignore[reportInvalidTypeArguments, reportAssignmentType]
    _env_history: "np.ndarray[np.float64]" = None # pyright: ignore[reportInvalidTypeArguments, reportAssignmentType]
    _PLS_BETA: "np.ndarray[np.float32]" = model['coeff'] # pyright: ignore[reportInvalidTypeArguments, reportAssignmentType]
    
    
    _rates_buffer = []
    _filename: str | None = None
    _suffix: int | None = None

    orientation: "np.ndarray[np.float32]" = np.zeros(3, dtype=np.float32) # pyright: ignore[reportInvalidTypeArguments, reportAssignmentType]
    wrist_orientation: "np.ndarray[np.float32]" = np.zeros(3, dtype=np.float32) # pyright: ignore[reportInvalidTypeArguments, reportAssignmentType]
    _omega: "np.ndarray[np.float32]" = np.zeros(2, dtype=np.float32) # pyright: ignore[reportInvalidTypeArguments, reportAssignmentType]
    _delta_omega: "np.ndarray[np.float32]" = np.zeros(2, dtype=np.float32) # pyright: ignore[reportInvalidTypeArguments, reportAssignmentType]
    _omega_gain: "np.ndarray[np.float32]" = np.array([0.02, 0.02], dtype=np.float32) # pyright: ignore[reportInvalidTypeArguments, reportAssignmentType]
    _omega_threshold: "np.ndarray[np.float32]" = np.array([0.02, 0.015], dtype=np.float32) # pyright: ignore[reportInvalidTypeArguments, reportAssignmentType]
    # _omega_threshold: "np.ndarray[np.float32]" = np.array([0.015, 0.01], dtype=np.float32)
    cluster_selection_window: ClusterSelectionWindow | None = None
    _filter_state_hpf = None
    _sos_hpf = None
    filter_cutoff_spikes = 5.0 # Hz
    _montage = None
    _acc_channels: Tuple[int, int, int] = [20, 21, 22] # pyright: ignore[reportAssignmentType]
    _gyro_channels: Tuple[int, int, int] = [23, 24, 25] # pyright: ignore[reportAssignmentType]
    _gyro_channel_scalar: float | None = None
    _alpha: float = 0.98 # gain on gyro contribution to orientation; accelerometer contribution is 1-_alpha.
    _beta: float = 0.020
    _wrist_orientation_estimate_gain: float = 1.0
    _recording: bool = False
    _has_muaps: bool = False
    _logger: BinaryLogger | None = None
    _logger_file: str | None = None
    _batch = 0
    _sample = 0
    _env_buffer_size: int = 16384
    _has_rates_model: bool = False
    _collecting_rates_model: bool = False
    _rates_model: "np.ndarray[np.float32]" = None # pyright: ignore[reportInvalidTypeArguments, reportAssignmentType]
    _dx: float = 0.0
    _x: float = 0.0
    _dy: float = 0.0
    _y: float = 0.0
    _xt: float = 0.0
    _yt: float = 0.0
    _button: bool = False
    _x_offset: float = 0.4
    _y_offset: float = 0.0
    _x_degrees: float = 20.0
    _y_degrees: float = 20.0
    _xrange: Tuple[float, float] = [2.515625, 3.34375] # pyright: ignore[reportAssignmentType]
    _yrange: Tuple[float, float] = [3.5625, 4.375] # pyright: ignore[reportAssignmentType]
    _omega_limit: float = 0.11*np.pi
    _montage_mode: int = 2 # 2 = del2 | 1 = SD | 0 = monopolar

    _sample_update_timer: QTimer | None = None
    _sample_timer_period = 5 # milliseconds

    _xy_interpolant_timer: QTimer | None = None
    _xy_interpolant_timer_period: int = 2 # milliseconds

    def __init__(self, board_shim, buffer_size, num_channels: int=35, 
                 filter_cutoff_env: float=1.0, filter_cutoff_hpf: float=100.0, filter_order: int=1, 
                 sample_rate=500, channel: int=None, threshold: float=None, 
                 pre_peak_samples: int=6, post_peak_samples: int=9, num_ipts: int = 12, 
                 compute_thresholds: bool = True, do_spike_detection: bool = True, 
                 spike_handler_cls=BeamformerSpikeHandler):
        super(Processor, self).__init__()
                # Initialize decode mode from model config (if valid)
        try:
            self._decode_mode = ProcessorMode(int(model["mode"]))
        except Exception:
            # Fallback: angular velocity mode
            self._decode_mode = ProcessorMode.ANGULAR_VELOCITY
        self.board_shim = board_shim
        self.buffer_size = buffer_size
        self.num_channels = num_channels
        self.sample_rate = sample_rate
        self.filter_cutoff_hpf = filter_cutoff_hpf
        self.filter_cutoff_env = filter_cutoff_env
        self.filter_order = filter_order
        self._gyro_channel_scalar = 0.00025 * (1/sample_rate)
        self.spikes = spike_handler_cls(self, 
                 buffer_size = buffer_size, 
                 pre_peak_samples = pre_peak_samples,
                 post_peak_samples = post_peak_samples, 
                 enable = do_spike_detection, 
                 compute_thresholds = compute_thresholds, 
                 num_ipts = num_ipts, 
                 channel=channel, 
                 threshold=threshold)
        self.spikes.detected.connect(self.spike.emit)
        self.spikes.embedding.connect(self.embedding.emit)
        self.parameter_socket = ParameterSocket(num_channels=num_ipts, scale_factor=100.0)
        self.stream_socket = StreamSocket()

        # Initialize buffers
        self.circular_buffer = np.zeros((num_channels, buffer_size)).astype(np.float64)
        self._env_history = np.zeros((9, self._env_buffer_size)).astype(np.float64)
        
        # Initialize filter states and design the highpass filter
        self._initialize_filter()
        self.set_montage(self._montage_mode)
        self._rates_x = np.ones(num_ipts+1, dtype=np.float32)
        self._xy_interpolant_timer = QTimer()
        self._xy_interpolant_timer.timeout.connect(self._interpolate_xy)
        self._sample_update_timer = QTimer()
        self._sample_update_timer.timeout.connect(self.sample_device)
        # Decoder encapsulating decoding logic
        self._decoder = Decoder(self)

    def update(self, new_data):
        """
        Core update method called to add new data to the circular buffer and applies highpass filter to the first 8 channels.
        """
        num_samples = new_data.shape[1]
        if num_samples < 1:
            return None
        sample = (self._sample + num_samples) % 32768
        batch = (self._batch + 1) % 32768
        self._sample = sample
        self._batch = batch

        # Apply highpass filter to the first 8 channels
        filtered_data = np.zeros((8, num_samples))
        for i in range(8):
            filtered_data[i, :], self._filter_state_hpf[i, :] = sosfilt(self._sos_hpf, new_data[i, :], zi=self._filter_state_hpf[i, :]) # pyright: ignore[reportOptionalSubscript]

        # Apply Spatial Referencing
        spatial_ref_data = np.zeros((8, num_samples))
        if self._montage_mode > 0:
            for j in range(8):
                neighbors_mean = np.mean([filtered_data[neighbor] for neighbor in self._montage[j]], axis=0) # pyright: ignore[reportOptionalSubscript]
                spatial_ref_data[j] = filtered_data[j] - neighbors_mean
        elif self._montage_mode == 0:
            # spatial_cmr = np.median(filtered_data, axis=0)
            for j in range(8):
                spatial_ref_data[j] = filtered_data[j]

        env_data = np.ones((9, num_samples))
        for k in range(8):
            env_data[k+1, :], self._filter_state_env[k, :] = sosfilt(self._sos_env, np.abs(spatial_ref_data[k,:]), zi=self._filter_state_env[k, :])
        
        acc_data = np.mean(new_data[self._acc_channels, :], axis=1) # Extract accelerometer channels (shape: 3 x num_samples)
        gyro_contribution = np.sum(new_data[self._gyro_channels, :] * self._gyro_channel_scalar, axis=1)
        acc_contribution = np.zeros(3)
        acc_contribution[0] = np.arctan2(acc_data[1], acc_data[2])
        acc_contribution[1] = np.arctan2(-acc_data[0], np.sqrt(acc_data[1]**2 + acc_data[2]**2))

        # Update orientation at wristband:
        self.orientation = self._alpha * (gyro_contribution + self.orientation) + self._beta * acc_contribution

        # Based on wristband rotation, update orientation at the wrist:
        self.wrist_orientation = self._alpha * (gyro_contribution * self._wrist_orientation_estimate_gain + self.wrist_orientation) + self._beta * acc_contribution * self._wrist_orientation_estimate_gain
        
        # Update the circular buffer
        self.circular_buffer[:, :-num_samples] = self.circular_buffer[:, num_samples:]
        self.circular_buffer[:8, -num_samples:] = spatial_ref_data
        self.circular_buffer[8:, -num_samples:] = new_data[8:, :]

        # Update the (longer-term) envelope history buffer
        num_env_samples = min(num_samples, self.buffer_size)
        self._env_history[:, :-num_env_samples] = self._env_history[:, num_env_samples:]
        self._env_history[1:9, -num_env_samples:] = env_data[1:9, -num_env_samples:]  # Store squared envelope values

        # Do any spike detection
        self.spikes.update(batch, sample, num_samples, spatial_ref_data)

        if self._decoder is not None and self._decode_mode is not ProcessorMode.OFF:
            self._decoder.step(env_data)

        # if self._has_rates_model:
        #     self.stream_socket.send_rates(self._rates_x[1:], scale_factor=100) 
        #     self._delta_omega = self._rates_x @ self._PLS_BETA
        #     omega_prev = np.copy(self._omega)
        #     self._omega[0] = min(max(self._omega[0] + self._delta_omega[0] * self._omega_gain[0],-self._omega_limit),self._omega_limit)
        #     self._omega[1] = min(max(self._omega[1] + self._delta_omega[1] * self._omega_gain[1],-self._omega_limit),self._omega_limit)
        #     delta_omega = self._omega - omega_prev
        #     global_env_power = np.mean(self._env_history)
        #     self.delta_omega.emit(-delta_omega[1], delta_omega[0], global_env_power, self.wrist_orientation[0])
        # else:
        #     if self._decode_mode is ProcessorMode.ANGULAR_VELOCITY:
        #         # angular velocity
        #         self._delta_omega = env_data.T @ self._PLS_BETA
        #         self._omega[0] = min(
        #             max(
        #                 self._omega[0]
        #                 + np.sum(
        #                     np.where(
        #                         np.abs(self._delta_omega[:, 0]) > self._omega_threshold[0],
        #                         self._delta_omega[:, 0],
        #                         0,
        #                     )
        #                 )
        #                 * self._omega_gain[0],
        #                 -self._omega_limit,
        #             ),
        #             self._omega_limit,
        #         )
        #         self._omega[1] = min(
        #             max(
        #                 self._omega[1]
        #                 + np.sum(
        #                     np.where(
        #                         np.abs(self._delta_omega[:, 1]) > self._omega_threshold[1],
        #                         self._delta_omega[:, 1],
        #                         0,
        #                     )
        #                 )
        #                 * self._omega_gain[1],
        #                 -self._omega_limit,
        #             ),
        #             self._omega_limit,
        #         )
        #         self.omega.emit(self._omega, env_data, self._omega_threshold, self._omega_gain, self._has_rates_model)

        #     elif self._decode_mode is ProcessorMode.ANGULAR_ACCELERATION:
        #         # angular acceleration
        #         delta_delta_omega = env_data.T @ self._PLS_BETA
        #         self._delta_omega[0] += min(
        #             max(
        #                 np.sum(
        #                     np.where(
        #                         np.abs(delta_delta_omega[:, 0]) > self._omega_threshold[0] * 0.001,
        #                         delta_delta_omega[:, 0],
        #                         0,
        #                     )
        #                 ),
        #                 -0.1 * self._omega_limit,
        #             ),
        #             0.1 * self._omega_limit,
        #         )
        #         self._delta_omega[1] += min(
        #             max(
        #                 np.sum(
        #                     np.where(
        #                         np.abs(delta_delta_omega[:, 1]) > self._omega_threshold[1] * 0.001,
        #                         delta_delta_omega[:, 1],
        #                         0,
        #                     )
        #                 ),
        #                 -0.1 * self._omega_limit,
        #             ),
        #             0.1 * self._omega_limit,
        #         )
        #         self._omega[0] = min(
        #             max(
        #                 self._omega[0]
        #                 + np.sum(
        #                     np.where(
        #                         np.abs(self._delta_omega[0]) > self._omega_threshold[0],
        #                         self._delta_omega[0],
        #                         0,
        #                     )
        #                 )
        #                 * self._omega_gain[0],
        #                 -self._omega_limit,
        #             ),
        #             self._omega_limit,
        #         )
        #         self._omega[1] = min(
        #             max(
        #                 self._omega[1]
        #                 + np.sum(
        #                     np.where(
        #                         np.abs(self._delta_omega[1]) > self._omega_threshold[1],
        #                         self._delta_omega[1],
        #                         0,
        #                     )
        #                 )
        #                 * self._omega_gain[1],
        #                 -self._omega_limit,
        #             ),
        #             self._omega_limit,
        #         )
        #         self.omega.emit(self._omega, env_data, self._omega_threshold, self._omega_gain, self._has_rates_model)

        #     elif self._decode_mode is ProcessorMode.ANGULAR_VELOCITY_UNBOUNDED:
        #         # angular velocity; no bounding
        #         self._delta_omega = env_data.T @ self._PLS_BETA
        #         delta_omega_x = np.sum(
        #             np.where(
        #                 np.abs(self._delta_omega[:, 0]) > self._omega_threshold[0],
        #                 self._delta_omega[:, 0],
        #                 0,
        #             )
        #         )
        #         delta_omega_y = np.sum(
        #             np.where(
        #                 np.abs(self._delta_omega[:, 1]) > self._omega_threshold[1],
        #                 self._delta_omega[:, 1],
        #                 0,
        #             )
        #         )
        #         self._omega[0] = self._omega[0] + delta_omega_x
        #         self._omega[1] = self._omega[1] + delta_omega_y

        #         global_env_power = np.mean(self._env_history)
        #         self.delta_omega.emit(delta_omega_x, delta_omega_y, global_env_power, self.wrist_orientation[0])

        #     elif self._decode_mode is ProcessorMode.ANGULAR_VELOCITY_ROBOT:
        #         # angular velocity for robot/LSL, with bounding & rotated axes
        #         self._delta_omega = env_data.T @ self._PLS_BETA
        #         omega_prev = np.copy(self._omega)
        #         self._omega[0] = min(
        #             max(
        #                 self._omega[0]
        #                 + np.sum(
        #                     np.where(
        #                         np.abs(self._delta_omega[:, 0]) > self._omega_threshold[0],
        #                         self._delta_omega[:, 0],
        #                         0,
        #                     )
        #                 )
        #                 * self._omega_gain[0],
        #                 -self._omega_limit,
        #             ),
        #             self._omega_limit,
        #         )
        #         self._omega[1] = min(
        #             max(
        #                 self._omega[1]
        #                 + np.sum(
        #                     np.where(
        #                         np.abs(self._delta_omega[:, 1]) > self._omega_threshold[1],
        #                         self._delta_omega[:, 1],
        #                         0,
        #                     )
        #                 )
        #                 * self._omega_gain[1],
        #                 -self._omega_limit,
        #             ),
        #             self._omega_limit,
        #         )
        #         delta_omega = self._omega - omega_prev
        #         global_env_power = np.mean(self._env_history)
        #         # Note the rotated / sign-flipped output you already had
        #         self.delta_omega.emit(-delta_omega[1], delta_omega[0], global_env_power, self.wrist_orientation[0])

        # If we are recording, save data to binary disk file.
        if self._recording:
            self._logger.write_batch(spatial_ref_data.T, 
                                     self._batch, 
                                     self._sample, 
                                     self._x, self._y, 
                                     float(self.orientation[0]), 
                                     self._button)


    def get_covariates(self) -> Tuple[float, float, float, bool]:
        return (self._x, self._y, float(self.orientation[0]), self._button)

    def start_device_sampling(self):
        self._sample_update_timer.start(self._sample_timer_period)

    def stop_device_sampling(self):
        self._sample_update_timer.stop()

    def start_xy_interpolation(self):
        self._xy_interpolant_timer.start(self._xy_interpolant_timer_period)

    def stop_xy_interpolation(self):
        self._xy_interpolant_timer.stop()

    def sample_device(self):
        """Get new data from the device, into our software buffer."""
        board_data = self.board_shim.get_board_data()
        if board_data is not None:
            self.update(board_data)

    def _interpolate_xy(self):
        x = 0.75 * self._x + 0.25 * self._xt
        y = 0.75 * self._y + 0.25 * self._yt
        self._dx = self._x - x
        self._x = x
        self._dy = self._y - y
        self._y = y

    def _initialize_filter(self):
        nyquist = 0.5 * self.sample_rate
        cutoff_norm = self.filter_cutoff_hpf / nyquist
        cutoff_env = self.filter_cutoff_env / nyquist
        self._sos_hpf = butter(self.filter_order, cutoff_norm, btype='high', output='sos')
        self._filter_state_hpf = np.array([sosfilt_zi(self._sos_hpf) for _ in range(8)])  # Initial states for 8 channels
        self._sos_env = butter(self.filter_order, cutoff_env, btype='low', output='sos')
        self._filter_state_env = np.array([sosfilt_zi(self._sos_env) for _ in range(8)])  # Initial states for 8 channels

    @pyqtSlot(int)
    def set_montage(self, mode: int = 2):
        """Sets the spatial reference montage for EMG channels.
        
        0: Monopolar
        1: Single-Differential
        2: Discrete Spatial Laplacian (default)
        """
        self._montage_mode = mode
        if mode == 2:
            self._montage = [
                    [1, 7],  # Channel 0 has neighbors 1 and 7
                    [0, 2],  # Channel 1 has neighbors 0 and 2
                    [1, 3],  # Channel 2 has neighbors 1 and 3
                    [2, 4],  # Channel 3 has neighbors 2 and 4
                    [3, 5],  # Channel 4 has neighbors 3 and 5
                    [4, 6],  # Channel 5 has neighbors 4 and 6
                    [5, 7],  # Channel 6 has neighbors 5 and 7
                    [6, 0]   # Channel 7 has neighbors 6 and 0
                ]
        elif mode == 1:
            self._montage = [[1], [2], [3], [4], [5], [6], [7], [0]]
        else:
            self._montage = [[], [], [], [], [], [], [], []]

    def update_position(self, x_in: float, y_in: float, button_state: bool):
        self._xt = Processor.remap(x_in, self._xrange, self._x_offset, self._x_degrees)
        self._yt = Processor.remap(y_in, self._yrange, self._y_offset, self._y_degrees)
        self._button = button_state

    def update_rates_buffer(self, rates):
        """
        Stores historical movement and coefficient data for directional trend analysis.
        """
        self._rates_x[1:] = rates
        self._rates_buffer.append({
            "x": self._dx, 
            "y": self._dy, 
            "sample": rates
        })

    @pyqtSlot(object)
    def on_model_update(self, new_coefficients: "np.ndarray[np.float32]"): # pyright: ignore[reportInvalidTypeArguments, reportAssignmentType]
        self._PLS_BETA = new_coefficients

    def start_emg_only_recording(self, fname_emg: str, fname_rates: str = None):
        self._recording = True
        self._logger = BinaryLogger(fname_emg)
        self._logger_file = fname_emg
        if fname_rates is not None and self.spikes.enabled:
            self.spikes.start_recording(fname_rates)

    def stop_emg_only_recording(self):
        self._recording = False
        self._logger.close()
        del self._logger
        self._logger = None
        r = BinaryReader(self._logger_file)
        r.convert()
        r.close()
        del r
        self._logger_file = None
        if self.spikes.enabled:
            self.spikes.stop_recording()

    @pyqtSlot(float)
    def update_omega_limit(self, base_gain: float):
        self._omega_limit = 0.11*np.pi / base_gain

    @pyqtSlot(object)
    def update_omega_deadzone(self, new_threshold: "np.ndarray[np.float32]"): # pyright: ignore[reportInvalidTypeArguments, reportAssignmentType]
        self._omega_threshold = new_threshold

    def get(self) -> NDArray[np.float64]:
        return self.circular_buffer # pyright: ignore[reportReturnType]
    
    def set_mode(self, mode: int | ProcessorMode):
        """
        Set the decode mode.

        Accepts either:
        - an int in [0, 4], for backward compatibility, or
        - a ProcessorMode enum.
        """
        if isinstance(mode, ProcessorMode):
            self._decode_mode = mode
            return

        # Backward-compatible int handling
        if (mode < 0) or (mode > 4):
            raise Exception("mode must be integer from 0 to 4!")
        self._decode_mode = ProcessorMode(mode)
    
    def set_orientation(self, new_orientation = None):
        """Sets the zero values for orientation."""
        if new_orientation is None:
            self.orientation = np.zeros(3)
        else:
            self.orientation -= new_orientation

    def set_alpha(self, new_alpha):
        """Set new value for alpha and beta coefficients."""
        self._alpha = new_alpha
        self._beta = 1 - new_alpha
    
    @pyqtSlot(bool)
    def handle_rates_model_checkbox_click(self, checked: bool):
        if checked:
            self._collecting_rates_model = True
        else:
            self._collecting_rates_model = False
            if len(self._rates_buffer) > 100:
                tmp_name = self._filename.replace('data/', '').replace('\\','/')
                def_name = f"{tmp_name}_{self._suffix}_rates_model"
                mdl, mdl_path = ModelInteractor.perform_pls_regression(self._rates_buffer, n=4, def_name=def_name) # pyright: ignore[reportGeneralTypeIssues]
                saved_rates = mdl_path is not None
                if saved_rates:
                    self._rates_model = mdl
                    muap_filters_fname = mdl_path.replace("_rates_model", "_muap_filters")
                    self.spikes.save_muap_filters_and_thresholds(muap_filters_fname)
                else:
                    self._rates_model = None
                self._rates_buffer = []
                self._has_rates_model = saved_rates
            else:
                self._rates_buffer = []
                self._has_rates_model = False
                print("Insufficient samples. Rates model cleared.")

    def set_filename(self, filename: str, suffix: int):
        self._filename = filename
        self._suffix = suffix

    @staticmethod
    def remap(data: float, data_lims: Tuple[float, float], output_offset: float = 0.0, output_gain: float = 20.0) -> float:
        """
        Returns data remapped between -1.0 and 1.0 based on data limits.
        """
        data_c = (data_lims[0] + data_lims[1])/2
        data_r = (data_lims[1] - data_lims[0])/2
        return ((data - data_c) / data_r + output_offset) * output_gain

    def __del__(self):
        try:
            self._sample_update_timer.stop()
        except Exception:
            pass

        try:
            self._xy_interpolant_timer.stop()
        except Exception:
            pass

        try:
            if self.board_shim.is_prepared():
                self.board_shim.release_session()  # Clean up the board session
        except Exception:
            print("[Processor]::Board session already released.")