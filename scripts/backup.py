import subprocess
import sys
from datetime import datetime
import os
import argparse

# Directory where generated SQL dumps are saved.
BACKUP_DIR = os.getenv("BACKUP_DIR", "./backups")

# Docker container name that runs PostgreSQL.
# This must match the actual container name in your compose setup.
CONTAINER_NAME = os.getenv("DB_CONTAINER_NAME", "group6_image_hosting_server-db-1")

# Database connection details passed to pg_dump/psql inside the container.
DB_NAME = os.getenv("DB_NAME", "group6_image_hosting_server_db")
DB_USER = os.getenv("DB_USER", "postgres")

# Create a new database dump using `pg_dump` executed inside the Postgres container.
# Produces a file like: backups/backup_YYYY-MM-DD_HHMMSS.sql
def create_backup():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"backup_{timestamp}.sql"
    filepath = os.path.join(BACKUP_DIR, filename)

    os.makedirs(BACKUP_DIR, exist_ok=True)

    cmd = [
        # Run commands inside the running postgres container.
        "docker", "exec", CONTAINER_NAME,
        # Dump database schema + data as SQL text.
        "pg_dump", "-U", DB_USER, "-d", DB_NAME
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        with open(filepath, 'w') as f:
            f.write(result.stdout)
        print(f"✅ Backup created: {filename}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating backup: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


# List all .sql files in BACKUP_DIR to help choose a restore target.
def list_backups():
    if not os.path.exists(BACKUP_DIR):
        print(f"The directory {BACKUP_DIR} does not exist.")
        return

    files = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.sql')])

    if not files:
        print("📂  No backups found")
        return

    print(f"✅ Backups found: {len(files)}")
    print("-" * 40)

    for file in files:
        print(f"📄 {file}")


# Restore a backup by piping the SQL dump into `psql` inside the postgres container.
# NOTE: This script does not apply any safety checks; restoring overwrites state
# according to what the dump contains.
def restore_backup(filename):
    if not filename.endswith('.sql'):
        filename += '.sql'

    filepath = os.path.join(BACKUP_DIR, filename)

    if not os.path.exists(filepath):
        print(f"File {filename} not found in {BACKUP_DIR}")
        sys.exit(1)

    with open(filepath, 'r') as f:
        sql_content = f.read()

    cmd = [
        # `-i` keeps stdin open for piping sql_content.
        "docker", "exec", "-i", CONTAINER_NAME,
        # Run psql against the target DB and read commands from stdin.
        "psql", "-U", DB_USER, "-d", DB_NAME
    ]

    try:
        subprocess.run(cmd, input=sql_content, text=True, check=True)
        print(f"✅ The database has been restored from backup: {filename}")
    except subprocess.CalledProcessError as e:
        print(f"Restore error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


# Simple CLI wrapper:
#   - `create`  -> create a new pg_dump file
#   - `list`    -> list available dump files
#   - `restore` -> restore a chosen dump file into the DB
def main():
    parser = argparse.ArgumentParser(
        description="PostgreSQL database backup script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        'command',
        choices=['create', 'list', 'restore'],
        help='Command to execute'
    )

    parser.add_argument(
        'filename',
        nargs='?',
        help='File name for restoration (only for the restore command)'
    )

    args = parser.parse_args()

    if args.command == "create":
        create_backup()
    elif args.command == "list":
        list_backups()
    elif args.command == "restore":
        if not args.filename:
            print("Enter the name of the file to restore")
            sys.exit(1)
        restore_backup(args.filename)


if __name__ == "__main__":
    main()
