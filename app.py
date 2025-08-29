\
import os
import sqlite3
import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Postulantes – Demo SQLite", page_icon="📚", layout="wide")

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "app.db")

SCHEMA_SQL = '''
CREATE TABLE IF NOT EXISTS postulantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    carrera TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    periodo TEXT NOT NULL,
    fecha_registro TEXT NOT NULL
);
'''

@st.cache_resource(show_spinner=False)
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(SCHEMA_SQL)
    return conn

def query_df(sql: str, params: tuple = ()):
    conn = get_conn()
    cur = conn.execute(sql, params)
    cols = [c[0] for c in cur.description] if cur.description else []
    rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)

def exec_sql(sql: str, params: tuple = ()):
    conn = get_conn()
    cur = conn.execute(sql, params)
    conn.commit()
    return cur.lastrowid

from typing import Optional

def exists_email(email: str, ignore_id: Optional[int] = None) -> bool:
    if ignore_id is None:
        df = query_df("SELECT id FROM postulantes WHERE email = ?", (email,))
    else:
        df = query_df("SELECT id FROM postulantes WHERE email = ? AND id != ?", (email, ignore_id))
    return not df.empty

def sidebar_form():
    st.sidebar.header("➕ Insertar nuevo postulante")
    with st.sidebar.form("new_form", clear_on_submit=True):
        nombre = st.text_input("Nombre completo *")
        carrera = st.selectbox("Carrera *", ["Big Data", "Desarrollo de Software", "Administración", "Redes", "Contabilidad"])
        email = st.text_input("Email *")
        periodo = st.text_input("Periodo *", value="2025-II")
        submitted = st.form_submit_button("Guardar")
        if submitted:
            if not (nombre and carrera and email and periodo):
                st.sidebar.error("Completa todos los campos marcados con *")
                return
            if exists_email(email):
                st.sidebar.error("El email ya existe. Usa otro.")
                return
            now = datetime.datetime.utcnow().isoformat()
            exec_sql(
                "INSERT INTO postulantes (nombre, carrera, email, periodo, fecha_registro) VALUES (?,?,?,?,?)",
                (nombre, carrera, email, periodo, now)
            )
            st.sidebar.success("Postulante insertado correctamente ✅")

def edit_modal(row):
    st.markdown("### ✏️ Editar postulante")
    with st.form(f"edit_{row['id']}"):
        nombre = st.text_input("Nombre completo *", value=row["nombre"])
        carrera = st.selectbox("Carrera *", ["Big Data", "Desarrollo de Software", "Administración", "Redes", "Contabilidad"], index=["Big Data", "Desarrollo de Software", "Administración", "Redes", "Contabilidad"].index(row["carrera"]) if row["carrera"] in ["Big Data", "Desarrollo de Software", "Administración", "Redes", "Contabilidad"] else 0)
        email = st.text_input("Email *", value=row["email"])
        periodo = st.text_input("Periodo *", value=row["periodo"])
        col1, col2 = st.columns(2)
        with col1:
            save = st.form_submit_button("💾 Guardar cambios")
        with col2:
            delete = st.form_submit_button("🗑️ Eliminar", type="secondary")
    if save:
        if not (nombre and carrera and email and periodo):
            st.error("Completa todos los campos marcados con *")
            return
        if exists_email(email, ignore_id=int(row["id"])):
            st.error("El email ya existe en otro registro.")
            return
        exec_sql(
            "UPDATE postulantes SET nombre=?, carrera=?, email=?, periodo=? WHERE id=?",
            (nombre, carrera, email, periodo, int(row["id"]))
        )
        st.success("Actualizado ✅")
        st.experimental_rerun()
    if delete:
        exec_sql("DELETE FROM postulantes WHERE id=?", (int(row["id"]),))
        st.success("Eliminado ✅")
        st.experimental_rerun()

def main():
    st.title("📚 Postulantes – Demo SQLite + Streamlit")
    st.caption("Ejemplo mínimo para leer/insertar (CRUD) y desplegar en Streamlit Cloud.")
    sidebar_form()

    st.subheader("🔎 Búsqueda")
    c1, c2, c3 = st.columns([2,2,1])
    with c1:
        filtro_texto = st.text_input("Buscar por nombre o email")
    with c2:
        filtro_carrera = st.selectbox("Filtrar por carrera", ["(Todas)","Big Data","Desarrollo de Software","Administración","Redes","Contabilidad"])
    with c3:
        st.write("")
        st.write("")
        btn_refrescar = st.button("🔄 Refrescar")

    sql = "SELECT id, nombre, carrera, email, periodo, fecha_registro FROM postulantes"
    params = ()
    filtros = []
    if filtro_texto:
        filtros.append("(nombre LIKE ? OR email LIKE ?)")
        params += (f"%{filtro_texto}%", f"%{filtro_texto}%")
    if filtro_carrera and filtro_carrera != "(Todas)":
        filtros.append("carrera = ?")
        params += (filtro_carrera,)
    if filtros:
        sql += " WHERE " + " AND ".join(filtros)
    sql += " ORDER BY fecha_registro DESC"

    df = query_df(sql, params)

    st.write(f"Registros encontrados: **{len(df)}**")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("✏️ Editar / Eliminar")
    if df.empty:
        st.info("No hay registros para editar.")
    else:
        # Selector de fila por ID
        ids = df["id"].astype(int).tolist()
        sel_id = st.selectbox("Selecciona el ID a editar:", ids)
        sel_row = df[df["id"] == sel_id].iloc[0].to_dict()
        edit_modal(sel_row)

    st.markdown("---")
    st.subheader("⬆️ Carga masiva desde CSV (opcional)")
    csv_file = st.file_uploader("Selecciona un CSV con columnas: nombre,carrera,email,periodo", type=["csv"])
    if csv_file is not None:
        try:
            tmp = pd.read_csv(csv_file).fillna("")
            needed = {"nombre","carrera","email","periodo"}
            if not needed.issubset(set(map(str.lower, tmp.columns))):
                st.error("El CSV debe contener columnas: nombre, carrera, email, periodo")
            else:
                # Mapear por si hay mayúsculas/minúsculas
                cols = {c.lower(): c for c in tmp.columns}
                inserted = 0
                for _, r in tmp.iterrows():
                    nombre = r[cols["nombre"]]
                    carrera = r[cols["carrera"]]
                    email = r[cols["email"]]
                    periodo = r[cols["periodo"]]
                    if not (nombre and carrera and email and periodo):
                        continue
                    if exists_email(email):
                        continue
                    now = datetime.datetime.utcnow().isoformat()
                    exec_sql(
                        "INSERT INTO postulantes (nombre, carrera, email, periodo, fecha_registro) VALUES (?,?,?,?,?)",
                        (str(nombre), str(carrera), str(email), str(periodo), now)
                    )
                    inserted += 1
                st.success(f"Carga finalizada. Insertados: {inserted}")
                st.experimental_rerun()
        except Exception as e:
            st.error(f"Error al procesar CSV: {e}")

if __name__ == "__main__":
    main()
