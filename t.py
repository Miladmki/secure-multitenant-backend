import os

# لیست دقیق فایل‌هایی که می‌خوای جمع بشن
FILES_TO_COLLECT = [
    "app/main.py",
    "app/core/config.py",
    "app/core/database.py",
    "app/core/security.py",
    "app/models/user.py",
    "app/models/refresh_token.py",
    "app/api/v1/auth.py",
    "app/api/v1/users.py",
    "app/schemas/user.py",
    "tests/test_auth_basic.py",
    "tests/test_auth_flow.py",
    "tests/test_refresh_flow.py",
]

def collect_selected_files(output_file="project_code.txt"):
    with open(output_file, "w", encoding="utf-8") as out:
        for filepath in FILES_TO_COLLECT:
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    out.write(f"\n\n# ===== File: {filepath} =====\n")
                    out.write(content)
                except Exception as e:
                    out.write(f"\n\n# ===== File: {filepath} (ERROR reading: {e}) =====\n")
            else:
                out.write(f"\n\n# ===== File: {filepath} (NOT FOUND) =====\n")

if __name__ == "__main__":
    collect_selected_files(output_file="project_code.txt")
    print("✅ Selected files collected into project_code.txt")
