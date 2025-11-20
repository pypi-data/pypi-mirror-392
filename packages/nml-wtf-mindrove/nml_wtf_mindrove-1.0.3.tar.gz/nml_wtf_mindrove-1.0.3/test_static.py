from nml.spike_scope import SpikeScope

if __name__ == "__main__":
    x_o, y_o = SpikeScope.generate_source_plot_offsets(extension_factor = 16)
    print(x_o)
    print(y_o)