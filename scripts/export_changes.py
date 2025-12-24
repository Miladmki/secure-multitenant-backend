import os

BASE_DIR = r"D:\codes\secure-multitenant-backend"
OUTPUT_FILE = os.path.join(BASE_DIR, "changes_dump.txt")

FILES = [
    # changed files
    "tests/conftest.py",
    "app/core/config.py",
    "app/api/v1/auth.py",
    "app/api/v1/users.py",
    "app/models/__init__.py",
    "tests/test_roles.py",
    "tests/test_roles_permissions_tenants.py",
    # new files
    ".env",
    "requirements.txt",
    "CRITICAL_FIXES.md",
]

SEPARATOR = "\n" + "=" * 80 + "\n"


def read_file_safe(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"[ERROR] File not found: {path}"
    except Exception as e:
        return f"[ERROR] Could not read {path}: {e}"


def main():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for relative_path in FILES:
            full_path = os.path.join(BASE_DIR, relative_path)

            out.write(SEPARATOR)
            out.write(f"FILE: {relative_path}\n")
            out.write(SEPARATOR)

            content = read_file_safe(full_path)
            out.write(content.strip() + "\n")

    print(f"✅ All files exported successfully to:\n{OUTPUT_FILE}")


if __name__ == "__main__":
    main()
