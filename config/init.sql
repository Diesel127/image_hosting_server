-- This file is mounted into the PostgreSQL container as an init script:
--   ./config/init.sql -> /docker-entrypoint-initdb.d/init.sql
-- The official postgres image runs all *.sql files in this directory once
-- during initial database startup (when the data directory is empty).
--
-- Purpose:
--   Create the `images` table that stores metadata for uploaded image files.

CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    original_name TEXT NOT NULL,
    size INTEGER NOT NULL,
    file_type TEXT NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notes:
-- - `filename` is the server-side stored (unique) name (not the original client name).
-- - `file_type` stores the original extension (jpg/png/gif, etc.).