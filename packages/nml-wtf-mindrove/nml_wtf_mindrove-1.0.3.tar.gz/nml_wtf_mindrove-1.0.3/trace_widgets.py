import sys, importlib, pkgutil, traceback
import pyqtgraph.widgets as pw

print("=== TRACE: pyqtgraph.widgets submodules ===", flush=True)

for finder, mod_name, ispkg in pkgutil.walk_packages(pw.__path__, prefix="pyqtgraph.widgets."):
    print(f"[try] {mod_name}", flush=True)
    try:
        importlib.import_module(mod_name)
        print(f"[ok]  {mod_name}", flush=True)
    except Exception as e:
        print(f"[ERR] {mod_name}: {e}", flush=True)
        traceback.print_exc()
        break
