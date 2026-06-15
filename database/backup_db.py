import os
import zipfile
from datetime import datetime

DB_PATH = "database/app_data.db"
UPLOAD_DIR = "static/uploads"
BACKUP_DIR = "backups"

MAX_BACKUPS = 7

os.makedirs(BACKUP_DIR, exist_ok=True)


def create_backup():
    """Tạo file backup zip gồm DB + uploads"""

    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_name = f"backup_{now}.zip"
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zipf:

        # 1. Backup DB
        if os.path.exists(DB_PATH):
            zipf.write(DB_PATH, arcname="database/app_data.db")

        # 2. Backup folder uploads
        if os.path.exists(UPLOAD_DIR):
            for root, _, files in os.walk(UPLOAD_DIR):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, ".")
                    zipf.write(full_path, arcname=arcname)

    print(f"✅ Backup created: {backup_path}")

    return backup_path


def cleanup_old_backups():
    """Giữ lại tối đa MAX_BACKUPS file backup mới nhất"""

    files = [
        os.path.join(BACKUP_DIR, f)
        for f in os.listdir(BACKUP_DIR)
        if f.endswith(".zip")
    ]

    # sort theo thời gian tạo (cũ -> mới)
    files.sort(key=os.path.getmtime)

    # xóa file cũ nếu vượt quá giới hạn
    while len(files) > MAX_BACKUPS:
        old_file = files.pop(0)
        try:
            os.remove(old_file)
            print(f"🗑 Deleted old backup: {old_file}")
        except Exception as e:
            print(f"❌ Cannot delete {old_file}: {e}")


def backup():
    """Hàm chính: backup + cleanup"""

    create_backup()
    cleanup_old_backups()


if __name__ == "__main__":
    backup()