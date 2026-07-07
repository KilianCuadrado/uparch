from app.db.connection import get_connection


def folder_exists_for_user(folder_id: int, user_id: int) -> bool:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id FROM folders WHERE id = ? AND user_id = ?", (folder_id, user_id)
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def create_folder(user_id: int, name: str, parent_id: int | None) -> int:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO folders (user_id, name, parent_id) VALUES (?, ?, ?)",
            (user_id, name, parent_id),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def list_folders(user_id: int, parent_id: int | None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if parent_id is None:
            cursor.execute(
                """
                SELECT id, name, parent_id, created_at
                FROM folders
                WHERE user_id = ? AND parent_id IS NULL
                ORDER BY name
                """,
                (user_id,),
            )
        else:
            cursor.execute(
                """
                SELECT id, name, parent_id, created_at
                FROM folders
                WHERE user_id = ? AND parent_id = ?
                ORDER BY name
                """,
                (user_id, parent_id),
            )
        return cursor.fetchall()
    finally:
        conn.close()


def count_files_in_folder(folder_id: int, user_id: int) -> int:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT COUNT(*) as count FROM files WHERE folder_id = ? AND user_id = ?",
            (folder_id, user_id),
        ).fetchone()
        return row["count"] if row else 0
    finally:
        conn.close()


def count_subfolders(folder_id: int) -> int:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT COUNT(*) as count FROM folders WHERE parent_id = ?", (folder_id,)
        ).fetchone()
        return row["count"] if row else 0
    finally:
        conn.close()


def get_folder_by_id(folder_id: int, user_id: int):
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM folders WHERE id = ? AND user_id = ?", (folder_id, user_id)
        ).fetchone()
    finally:
        conn.close()


def delete_folder(folder_id: int):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
        conn.commit()
    finally:
        conn.close()


def rename_folder(folder_id: int, new_name: str):
    conn = get_connection()
    try:
        conn.execute("UPDATE folders SET name = ? WHERE id = ?", (new_name, folder_id))
        conn.commit()
    finally:
        conn.close()
