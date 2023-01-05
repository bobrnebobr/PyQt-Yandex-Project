import sqlite3

conn = sqlite3.connect("data/tracks_database.db")
cur = conn.cursor()


def create_or_get_database():
    cur.execute("""CREATE TABLE IF NOT EXISTS tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );""")
    cur.execute("""CREATE TABLE IF NOT EXISTS tracks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT,
        color TEXT DEFAULT "#FFFFFF",
        hotkey TEXT NULL,
        playlist_id INTEGER
    );""")
    conn.commit()


def get_all_tables():
    return cur.execute("SELECT name FROM tables").fetchall()[::-1]


def get_tracks(playlist_name, is_distinct):
    return cur.execute(f"""SELECT * FROM tracks WHERE playlist_id = (SELECT id FROM tables WHERE name = '{playlist_name}') {'GROUP BY path' * is_distinct}""").fetchall()[::-1]


def add_table(table_name):
    try:
        cur.execute(f"INSERT INTO tables(name) VALUES ('{table_name}');")
        conn.commit()
        return True
    except Exception as exc:
        if type(exc) == sqlite3.OperationalError:
            return "Неверное имя"
        elif type(exc) == sqlite3.IntegrityError:
            return "Данное имя уже занято"


def add_tracks(playlist_name, tracks):
    playlist_id = cur.execute(f"SELECT id FROM tables WHERE name = '{playlist_name}'").fetchall()[0][0]
    items = [(track_path, playlist_id) for track_path in tracks]
    print(items)
    cur.execute(f"INSERT INTO tracks(path, playlist_id) VALUES {str(items)[1:-1]}")
    conn.commit()


def add_rows(playlist_name, tracks):
    print(tracks)
    playlist_id = cur.execute(f"SELECT id FROM tables WHERE name = '{playlist_name}'").fetchall()[0][0]
    items = [(track[1], track[2], playlist_id) for track in tracks]
    print(items)
    try:
        cur.execute(f"INSERT INTO tracks(path, color, playlist_id) VALUES {str(items)[1:-1]}")
    except Exception as exc:
        pass
    conn.commit()


def delete_table(playlist_name):
    cur.execute(f"""DELETE FROM tracks WHERE playlist_id = (SELECT id FROM tables WHERE name = '{playlist_name}')""")
    cur.execute(f"""DELETE FROM tables WHERE name = '{playlist_name}'""")
    conn.commit()


def delete_audio(audio_id):
    cur.execute(f"""DELETE FROM tracks WHERE id = {audio_id}""")
    conn.commit()


def set_color(audio_id, color):
    cur.execute(f"""UPDATE tracks SET color = '{color}' WHERE id = {audio_id}""")
    conn.commit()


create_or_get_database()
