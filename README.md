# Streamlit + SQLite CRUD (Postulantes)

Demo mínima para **leer, insertar, actualizar y eliminar** registros en SQLite con **Streamlit**.
Lista para subir a **Streamlit Community Cloud**.

## Estructura

```
streamlit_sqlite_demo/
├─ app.py
├─ init_db.py
├─ requirements.txt
└─ data/
   └─ app.db   ← se crea/usa automáticamente
```

## Ejecutar localmente

```bash
pip install -r requirements.txt
python init_db.py      # opcional: inserta datos de ejemplo si la tabla está vacía
streamlit run app.py
```

## Despliegue en Streamlit Community Cloud

1. Sube este folder a un repositorio en GitHub (p.ej. `usuario/streamlit_sqlite_demo`).
2. Ve a https://share.streamlit.io/ y crea una nueva app apuntando a `app.py`.
3. La aplicación creará `data/app.db` si no existe. Los cambios persisten **mientras la app no se vuelva a construir** (en despliegues gratuitos, es común que se reinicie; para persistencia robusta considera un DB externo).
4. ¡Listo!

## Campos de la tabla `postulantes`

- `id` (INTEGER, PK, autoincrement)
- `nombre` (TEXT, requerido)
- `carrera` (TEXT, requerido)
- `email` (TEXT, requerido, único)
- `periodo` (TEXT, requerido)
- `fecha_registro` (TEXT ISO8601 UTC)

## Notas

- Todas las operaciones usan **consultas parametrizadas** (`?`) para evitar inyecciones SQL.
- `st.cache_resource` mantiene una única conexión SQLite por proceso.
- Incluye carga CSV masiva (columnas: `nombre,carrera,email,periodo`).

¡Éxitos! 🎓
