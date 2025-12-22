import os

# مسیر پایه پروژه
base_path = r"D:\codes\secure-multitenant-backend"

# لیست فایل‌های دسته ۲
files = [
    r"app\models\__init__.py",
    r"app\models\tenant.py",
    r"tests\test_roles.py",
]

# مسیر فایل خروجی
output_file = os.path.join(base_path, "category2.txt")

with open(output_file, "w", encoding="utf-8") as out:
    for file in files:
        file_path = os.path.join(base_path, file)
        out.write(f"===== {file} =====\n")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                out.write(f.read())
        except FileNotFoundError:
            out.write(f"[!] File not found: {file_path}\n")
        out.write("\n\n")

print(f"✅ Combined file saved to: {output_file}")
