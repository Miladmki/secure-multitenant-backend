# debug_import.py
from importlib import import_module
import sys

print("PYTHONPATH sample:", sys.path[:5])

try:
    m = import_module("app")
    print("import app ->", m)
    print("app.__file__:", getattr(m, "__file__", None))
    print("type(app):", type(m))
except Exception as e:
    print("import app failed:", repr(e))

try:
    mm = import_module("app.main")
    print("import app.main ->", mm)
    print("app.main.__file__:", getattr(mm, "__file__", None))
    print("has attr 'app'?:", hasattr(mm, "app"))
    print("type(mm.app):", type(getattr(mm, "app", None)))
    print("repr(mm.app):", repr(getattr(mm, "app", None)))
except Exception as e:
    print("import app.main failed:", repr(e))
