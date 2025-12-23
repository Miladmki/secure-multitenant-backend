import os
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SERVICE_DIR = os.path.join(PROJECT_ROOT, "app", "services")


@pytest.mark.parametrize(
    "filename", [f for f in os.listdir(SERVICE_DIR) if f.endswith(".py")]
)
def test_services_do_not_import_api(filename):
    """
    سرویس‌ها نباید چیزی از api import کنند.
    """
    with open(os.path.join(SERVICE_DIR, filename), "r", encoding="utf-8") as f:
        content = f.read()
        assert "app.api" not in content, f"{filename} imports api layer!"
        assert (
            "fastapi" not in content
        ), f"{filename} imports FastAPI (should be pure business logic)"
