import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
from nml.gui_window import GuiWindow
from emgdecomp.decomposition import EmgDecomposition


class EmgDecompositionVisualizer(GuiWindow):
    def __init__(self):
        super().__init__(set_layout=False)
        self._initialize_cmu_style()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.plot_widget = pg.GraphicsLayoutWidget()
        self.layout.addWidget(self.plot_widget)
        self.show()
    
    def plot_muaps(self, decomp: EmgDecomposition, data: np.ndarray, firings: np.ndarray, 
                   waveform_duration_ms: float = 40., n_rows: int = 2, n_cols: int = 3, 
                   fig_size=1.5, ylim: float = -.3e-3, only_average: bool = True):
        """
        Visualizes MUAP waveforms inside PyQt5 GUI.
        """
        self.plot_widget.clear()
        muaps = decomp.muap_waveforms(data=data, firings=firings, waveform_duration_ms=waveform_duration_ms)
        
        grid = self.plot_widget.addLayout()
        for key in muaps:
            muap = muaps[key].reshape((muaps[key].shape[0], n_rows, n_cols, muaps[key].shape[-1]))

            for i in range(n_rows):
                for j in range(n_cols):
                    plot = grid.addPlot(row=i, col=j)
                    plot.hideAxis('left')
                    plot.hideAxis('bottom')
                    plot.setYRange(-ylim, ylim)

                    if not only_average:
                        for trial in muap[:, i, j]:
                            plot.plot(trial, pen=pg.mkPen('k', width=1, style=pg.QtCore.Qt.DashLine))

                    avg_waveform = np.mean(muap[:, i, j], axis=0)
                    plot.plot(avg_waveform, pen=pg.mkPen('b', width=2))
                    plot.setTitle(f"ch {1 + i * n_cols + j}")
    
    def plot_firings(self, decomp: EmgDecomposition, data: np.ndarray, firings: np.ndarray):
        """
        Visualizes detected firings inside PyQt5 GUI.
        """
        self.plot_widget.clear()
        n_sources = len(decomp.model.components)
        projected = decomp.projected_data(data)
        gamma = np.power(projected, 2)

        plot = self.plot_widget.addPlot()
        plot.setLabel('left', 'Source Index')
        plot.setLabel('bottom', 'Time (s)')
        plot.addLegend()

        time_s = np.arange(gamma.shape[1]) / decomp.params.sampling_rate

        for i in range(gamma.shape[0]):
            norm_data = gamma[i, :] / (2 * np.max(gamma[i, :]))
            plot.plot(time_s, i + norm_data, pen=pg.mkPen('k', width=1, style=pg.QtCore.Qt.DashLine), name=f"Source {i}")

        for unit in range(n_sources):
            spike_times = firings['discharge_seconds'][firings['source_idx'] == unit]
            scatter = pg.ScatterPlotItem(spike_times, np.full_like(spike_times, unit), symbol='o', brush='r', size=5)
            plot.addItem(scatter)
    
    def plot_muaps_and_firings(self, decomp: EmgDecomposition, data: np.ndarray, firings: np.ndarray, 
                            waveform_duration_ms: float = 40., n_rows: int = 2, n_cols: int = 3, 
                            fig_size=1.5, ylim: float = -.3e-3, only_average: bool = True):
        """
        Efficiently visualizes MUAP waveforms and color-keyed firings together without clearing and re-adding plots.
        """
        muaps = decomp.muap_waveforms(data=data, firings=firings, waveform_duration_ms=waveform_duration_ms)
        
        if not hasattr(self, 'muap_plots'):
            self.muap_plots = {}  # Store persistent plot references
            self.firing_scatter_items = []
            self.firings_plot = None

        ### --- MUAPs Plot ---
        for key in muaps:
            muap = muaps[key].reshape((muaps[key].shape[0], n_rows, n_cols, muaps[key].shape[-1]))
            if key not in self.muap_plots:
                self.muap_plots[key] = {}

            for i in range(n_rows):
                for j in range(n_cols):
                    if (i, j) not in self.muap_plots[key]:
                        plot = self.plot_widget.addPlot(row=i, col=j)
                        plot.hideAxis('left')
                        plot.hideAxis('bottom')
                        plot.setYRange(-ylim, ylim)
                        plot.setTitle(f"ch {1 + i * n_cols + j}")
                        self.muap_plots[key][(i, j)] = {'plot': plot, 'avg_curve': None, 'trials': []}

                    plot_data = self.muap_plots[key][(i, j)]
                    if not only_average:
                        # Update or create trial plots
                        while len(plot_data['trials']) < muap.shape[0]:
                            curve = plot_data['plot'].plot(pen=pg.mkPen('k', width=1, style=pg.QtCore.Qt.DashLine))
                            plot_data['trials'].append(curve)

                        for trial_idx, trial_curve in enumerate(plot_data['trials']):
                            if trial_idx < muap.shape[0]:
                                trial_curve.setData(muap[trial_idx, i, j])
                            else:
                                trial_curve.hide()

                    # Update average MUAP
                    avg_waveform = np.mean(muap[:, i, j], axis=0)
                    if plot_data['avg_curve'] is None:
                        plot_data['avg_curve'] = plot_data['plot'].plot(pen=pg.mkPen('b', width=2))
                    plot_data['avg_curve'].setData(avg_waveform)

        ### --- Firings Plot ---
        if self.firings_plot is None:
            self.firings_plot = self.plot_widget.addPlot(row=n_rows, col=0, colspan=n_cols)
            self.firings_plot.setLabel('left', 'Source Index')
            self.firings_plot.setLabel('bottom', 'Time (s)')
            self.firings_plot.addLegend()

        n_sources = len(decomp.model.components)
        projected = decomp.projected_data(data)
        gamma = np.power(projected, 2)
        time_s = np.arange(gamma.shape[1]) / decomp.params.sampling_rate

        # Update projected data plots
        for i in range(gamma.shape[0]):
            norm_data = gamma[i, :] / (2 * np.max(gamma[i, :]))
            if len(self.firing_scatter_items) <= i:
                curve = self.firings_plot.plot(time_s, i + norm_data, pen=pg.mkPen('k', width=1, style=pg.QtCore.Qt.DashLine), name=f"Source {i}")
                self.firing_scatter_items.append(curve)
            else:
                self.firing_scatter_items[i].setData(time_s, i + norm_data)

        # Update or create scatter plots for firings
        for unit in range(n_sources):
            spike_times = firings['discharge_seconds'][firings['source_idx'] == unit]

            if len(self.firing_scatter_items) <= n_sources + unit:
                scatter = pg.ScatterPlotItem(spike_times, np.full_like(spike_times, unit), symbol='o', 
                                            brush=pg.intColor(unit, n_sources), size=5)
                self.firings_plot.addItem(scatter)
                self.firing_scatter_items.append(scatter)
            else:
                scatter = self.firing_scatter_items[n_sources + unit]
                scatter.setData(spike_times, np.full_like(spike_times, unit))
