import os

# مسیر پایه پروژه
base_path = r"D:\codes\secure-multitenant-backend"

# لیست فایل‌های دسته ۵
files = [
    r"tests\conftest.py",
    r"tests\merge_tests.py",
    r"tests\test_auth_basic.py",
    r"tests\test_auth_failures.py",
    r"tests\test_auth_flow.py",
    r"tests\test_imports.py",
    r"tests\test_refresh_flow.py",
    r"tests\test_roles_permissions_tenants.py",
    r"tests\test_roles.py",
    r"tests\test_service_dependencies.py",
    r"tests\test_tenant_isolation.py",
    r"tests\test_users_me.py",
    r"app\api\v1\users.py",
    r"app\core\security.py",
    r"app\core\deps.py",
    r"tests\conftest.py",  # دوباره در لیست آمده
]

# مسیر فایل خروجی
output_file = os.path.join(base_path, "category5.txt")

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
