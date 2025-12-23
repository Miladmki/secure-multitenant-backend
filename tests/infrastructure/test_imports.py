import os
import sys
import pytest
import importlib
import pkgutil

# مسیر پروژه
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)


def iter_modules(package):
    """تمام ماژول‌های یک پکیج را yield می‌کند"""
    package_path = package.__path__
    for _, name, ispkg in pkgutil.walk_packages(package_path, package.__name__ + "."):
        yield name


@pytest.mark.parametrize("module_name", list(iter_modules(importlib.import_module("app"))))
def test_no_circular_imports(module_name):
    """
    تست می‌کند که هیچ circular import یا وابستگی اشتباه وجود نداشته باشد.
    """
    try:
        importlib.import_module(module_name)
    except ImportError as e:
        pytest.fail(f"ImportError in {module_name}: {e}")
    except Exception as e:
        # اگر خطای RuntimeError مربوط به circular import بود
        if "circular" in str(e).lower():
            pytest.fail(f"Circular import detected in {module_name}: {e}")
