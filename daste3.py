import os

# مسیر پایه پروژه
base_path = r"D:\codes\secure-multitenant-backend"

# لیست فایل‌های دسته ۳
files = [
    r"app\api\v1\users.py",
    r"app\routers\admin.py",
    r"app\routers\tenant_dashboard.py",
    r"app\main.py",
]

# مسیر فایل خروجی
output_file = os.path.join(base_path, "category3.txt")

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
