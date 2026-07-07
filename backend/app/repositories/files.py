from app.db.connection import get_connection


def create_file_record(
    user_id: int,
    folder_id: int | None,
    filename: str,
    original_filename: str,
    size: int,
) -> int:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO files (user_id, folder_id, filename, original_filename, size)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, folder_id, filename, original_filename, size),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def list_files(user_id: int, folder_id: int | None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if folder_id is None:
            cursor.execute(
                "SELECT * FROM files WHERE user_id = ? AND folder_id IS NULL ORDER BY upload_time DESC",
                (user_id,),
            )
        else:
            cursor.execute(
                "SELECT * FROM files WHERE user_id = ? AND folder_id = ? ORDER BY upload_time DESC",
                (user_id, folder_id),
            )
        return cursor.fetchall()
    finally:
        conn.close()


def get_file_by_id(user_id: int, file_id: int):
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM files WHERE id = ? AND user_id = ?", (file_id, user_id)
        ).fetchone()
    finally:
        conn.close()


def delete_file(file_id: int):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
        conn.commit()
    finally:
        conn.close()


def move_file(file_id: int, folder_id: int | None):
    conn = get_connection()
    try:
        conn.execute("UPDATE files SET folder_id = ? WHERE id = ?", (folder_id, file_id))
        conn.commit()
    finally:
        conn.close()
