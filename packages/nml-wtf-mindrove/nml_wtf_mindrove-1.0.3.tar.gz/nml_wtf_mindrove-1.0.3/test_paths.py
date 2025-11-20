from nml.local_paths import paths
from nml.spike_scope import SpikeScope
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    # for k in paths.keys():
    #     print(f"{k}: {paths[k]}")
    app = QApplication(sys.argv)
    scope = SpikeScope()
    scope.show()
    sys.exit(app.exec_())
    