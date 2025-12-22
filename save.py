import os

# مسیر مقصد برای ذخیره فایل‌های txt
base_path = r"D:\codes\secure-multitenant-backend"

# دسته‌بندی فایل‌ها
categories = {
    "routing.txt": [
        "app/main.py",
        "app/api/v1/auth.py",
        "app/api/v1/users.py",
        "app/routers/admin.py",
        "app/routers/tenants.py",
        "app/routers/items.py",
    ],
    "dependencies.txt": [
        "app/core/deps.py",
        "app/core/utils.py",
    ],
    "models.txt": [
        "app/models/user.py",
        "app/models/role.py",
        "app/models/user_roles.py",
        "app/models/refresh_token.py",
        "app/models/tenant.py",
        "app/models/item.py",
    ],
    "database.txt": [
        "app/core/database.py",
        "alembic/env.py",
        # اگر migrationها پوشه جدا دارن می‌تونی کل پوشه رو هم بخونی
        "tests/conftest.py",
    ],
}


def save_code_lists():
    os.makedirs(base_path, exist_ok=True)
    for txt_name, file_list in categories.items():
        txt_path = os.path.join(base_path, txt_name)
        with open(txt_path, "w", encoding="utf-8") as out_file:
            for file_path in file_list:
                abs_path = os.path.join(base_path, file_path)
                out_file.write(f"\n# ===== {file_path} =====\n")
                if os.path.exists(abs_path):
                    with open(abs_path, "r", encoding="utf-8") as src:
                        out_file.write(src.read())
                else:
                    out_file.write(f"# ⚠ فایل {file_path} پیدا نشد.\n")
        print(f"✅ {txt_path} ساخته شد.")


if __name__ == "__main__":
    save_code_lists()
