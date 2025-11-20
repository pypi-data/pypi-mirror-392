import sys
print(">>> Starting QtGui import probe")

try:
    print(">>> import PyQt5.QtGui ...", end="", flush=True)
    from PyQt5 import QtGui
    print("OK")
except Exception as e:
    print("FAILED:", e)
    sys.exit()

# Now test specific classes AxisItem needs:
tests = [
    "QFont",
    "QPainterPath",
    "QTransform",
    "QColor",
    "QPen",
    "QBrush",
    "QPolygonF",
]

for name in tests:
    try:
        print(f">>> from PyQt5.QtGui import {name} ...", end="", flush=True)
        cls = getattr(QtGui, name)
        print("OK")
    except Exception as e:
        print(f"FAILED: {e}")
        break
