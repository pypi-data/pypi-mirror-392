import sys, importlib, pkgutil, traceback

print("=== TRACE: pyqtgraph import sequence ===")

def traced_import(name):
    print(f"[import] {name}", flush=True)
    return importlib.import_module(name)

try:
    # List modules inside pyqtgraph *before* importing it
    import pyqtgraph
    print("[TRACE] pyqtgraph top-level imported", flush=True)
        
    # Explicitly walk all submodules and import them one-by-one
    for finder, mod_name, ispkg in pkgutil.walk_packages(pyqtgraph.__path__, prefix="pyqtgraph."):
        print(f"[walk] trying {mod_name}", flush=True)
        try:
            importlib.import_module(mod_name)
            print(f"[ok] {mod_name}", flush=True)
        except Exception as e:
            print(f"[ERR] {mod_name}: {e}", flush=True)
            traceback.print_exc()
            break

    print("=== DONE ===", flush=True)

except Exception as e:
    print("!!! Fatal error before tracing submodules !!!", flush=True)
    traceback.print_exc()
