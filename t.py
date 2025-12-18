import pathlib

# لیست فایل‌هایی که می‌خواهی ترکیب کنی
files = [
    r"D:\codes\secure-multitenant-backend\tests\conftest.py",
    r"D:\codes\secure-multitenant-backend\tests\test_users_me.py",
    r"D:\codes\secure-multitenant-backend\tests\test_refresh_flow.py",
    r"D:\codes\secure-multitenant-backend\tests\test_auth_flow.py",
    r"D:\codes\secure-multitenant-backend\tests\test_auth_failures.py",
    r"D:\codes\secure-multitenant-backend\tests\test_auth_basic.py",
]

output_file = pathlib.Path(r"D:\codes\secure-multitenant-backend\tests\all_tests.txt")

with output_file.open("w", encoding="utf-8") as out:
    for f in files:
        path = pathlib.Path(f)
        out.write(f"===== {path.name} =====\n")
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as e:
            text = f"خطا در خواندن {f}: {e}"
        out.write(text)
        out.write("\n\n")
