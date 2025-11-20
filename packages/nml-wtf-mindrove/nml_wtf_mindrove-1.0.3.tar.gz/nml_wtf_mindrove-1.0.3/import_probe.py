import sys
import traceback
import os
os.environ["QT_OPENGL"] = "software"
os.environ["PYQTGRAPH_QT_LIB"] = "PyQt5"
print("""
      os.environ["QT_OPENGL"] = "software"
os.environ["PYQTGRAPH_QT_LIB"] = "PyQt5")
print(">>> import_probe: starting"
      """)

try:
    print(">>> importing PyQt5.QtWidgets.QApplication ...")
    from PyQt5.QtWidgets import QApplication
    print(">>> PyQt5 imported OK")
except Exception:
    print("!!! ERROR importing PyQt5")
    traceback.print_exc()
    sys.exit(1)

try:
    print(">>> importing PyQtGraph ...")
    import pyqtgraph as pg
    print(">>> PyQtGraph imported OK")
except Exception:
    print("!!! ERROR importing PyQtGraph")
    traceback.print_exc()
    sys.exit(1)

try:
    print(">>> importing nml.application.Application ...")
    from nml.application import Application
    print(">>> nml.application imported OK:", Application)
except Exception:
    print("!!! ERROR importing nml.application")
    traceback.print_exc()
    sys.exit(1)

print(">>> import_probe: all imports succeeded")
