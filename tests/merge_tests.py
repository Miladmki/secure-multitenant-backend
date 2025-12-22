import os

# مسیر پوشه تست‌ها (همون پوشه‌ای که اسکریپت داخلشه)
tests_dir = os.path.dirname(__file__)

# فایل‌های تستی که می‌خوای merge بشن
test_files = [
    "conftest.py",
    "test_auth_basic.py",
    "test_auth_failures.py",
    "test_auth_flow.py",
    "test_imports.py",
    "test_refresh_flow.py",
    "test_roles_permissions_tenants.py",
    "test_roles.py",
    "test_service_dependencies.py",
    "test_tenant_isolation.py",
    "test_users_me.py",
]

output_file = os.path.join(tests_dir, "all_tests.txt")

with open(output_file, "w", encoding="utf-8") as outfile:
    for fname in test_files:
        path = os.path.join(tests_dir, fname)
        if os.path.exists(path):
            outfile.write(f"\n\n# ===== {fname} =====\n\n")
            with open(path, "r", encoding="utf-8") as infile:
                outfile.write(infile.read())
        else:
            outfile.write(f"\n\n# ===== {fname} (NOT FOUND) =====\n\n")

print(f"✅ Merged {len(test_files)} files into {output_file}")
