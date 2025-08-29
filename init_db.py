import os, sqlite3, datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "app.db")

schema_sql = '''
CREATE TABLE IF NOT EXISTS postulantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    carrera TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    periodo TEXT NOT NULL,
    fecha_registro TEXT NOT NULL
);
'''

seed = [
    ("Ana Pérez", "Big Data", "ana.perez@example.com", "2025-II"),
    ("Carlos Ramírez", "Desarrollo de Software", "carlos.ramirez@example.com", "2025-II"),
    ("María López", "Administración", "maria.lopez@example.com", "2025-II"),
]

def main():
    os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(schema_sql)
    # Insert seed data if table is empty
    cur.execute("SELECT COUNT(*) FROM postulantes")
    count = cur.fetchone()[0]
    if count == 0:
        now = datetime.datetime.utcnow().isoformat()
        cur.executemany(
            "INSERT INTO postulantes (nombre, carrera, email, periodo, fecha_registro) VALUES (?,?,?,?,?)",
            [(n,c,e,p, now) for (n,c,e,p) in seed]
        )
    conn.commit()
    conn.close()
    print("DB inicializada en", DB_PATH)

if __name__ == "__main__":
    main()
