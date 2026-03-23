import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables from the `.env` file (if present).
load_dotenv()


class DatabaseManager:
    # Small wrapper around psycopg2 providing CRUD operations
    # for the `images` table.
    def __init__(self):
        self.connection = None

    def connect(self):
        try:
            # Create a new connection using env vars.
            self.connection = psycopg2.connect(
                host=os.getenv('DB_HOST'),
                database=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                port=os.getenv('DB_PORT')
            )
            print("✅ Connected to PostgreSQL")
        except Exception as e:
            print(f"Connection error: {e}")

    def disconnect(self):
        # Close the open connection on server shutdown.
        if self.connection:
            self.connection.close()
            print("Disconnected from PostgreSQL")

    def save_metadata(self, filename, original_name, size, file_type):
        try:
            # Insert a new row describing the uploaded file.
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO images (filename, original_name, size, file_type)
                    VALUES (%s, %s, %s, %s)
                """, (filename, original_name, size, file_type))
                self.connection.commit()
                return True
        except Exception as e:
            print(f"Save error: {e}")
            return False

    def get_all_images(self, page=1, per_page=10):
        try:
            # Fetch a single page ordered by newest uploads first.
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                offset = (page - 1) * per_page
                cursor.execute("""
                    SELECT * FROM images
                    ORDER BY upload_time DESC
                    LIMIT %s OFFSET %s
                """, (per_page, offset))
                images = cursor.fetchall()

                # Total count is used by the UI for pagination (if extended).
                cursor.execute("SELECT COUNT(*) FROM images")
                total = cursor.fetchone()['count']

                return images, total
        except Exception as e:
            print(f"Retrieval error: {e}")
            return [], 0

    def delete_image(self, image_id):
        try:
            # Delete a row by id, but first fetch filename so the server can
            # also remove the corresponding file from disk.
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT filename FROM images WHERE id = %s", (image_id,))
                result = cursor.fetchone()
                if not result:
                    return False

                filename = result[0]
                cursor.execute("DELETE FROM images WHERE id = %s", (image_id,))
                self.connection.commit()
                return filename
        except Exception as e:
            print(f"Delete error: {e}")
            return False
