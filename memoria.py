import os, sqlite3, json
from contextlib import contextmanager

DB_PATH = os.getenv("DB_PATH", "loteria_master_ai.db")
os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)

@contextmanager
def conectar():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def inicializar_db():
    with conectar() as conn:
        c=conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS resultados_verificados(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pais TEXT NOT NULL,
            loteria_clave TEXT NOT NULL,
            loteria_nombre TEXT NOT NULL,
            tipo_juego TEXT NOT NULL,
            fecha TEXT NOT NULL,
            resultado_json TEXT NOT NULL,
            estado TEXT NOT NULL,
            fuentes_json TEXT NOT NULL,
            creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(loteria_clave, fecha)
        )''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS capturas_fuente(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loteria_clave TEXT NOT NULL,
            fecha TEXT NOT NULL,
            fuente TEXT NOT NULL,
            resultado_json TEXT,
            estado TEXT NOT NULL,
            detalle TEXT,
            creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS predicciones_congeladas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_operativa TEXT NOT NULL,
            corte TEXT NOT NULL,
            loteria_clave TEXT NOT NULL,
            ranking_json TEXT NOT NULL,
            metadata_json TEXT,
            creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(fecha_operativa, corte, loteria_clave)
        )''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS evaluaciones(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_operativa TEXT NOT NULL,
            corte TEXT NOT NULL,
            loteria_clave TEXT NOT NULL,
            aciertos_top5 INTEGER DEFAULT 0,
            aciertos_top10 INTEGER DEFAULT 0,
            aciertos_top20 INTEGER DEFAULT 0,
            acertados_json TEXT,
            creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(fecha_operativa, corte, loteria_clave)
        )''')

def guardar_captura(clave, fecha, fuente, resultado, estado, detalle=""):
    with conectar() as conn:
        conn.execute('''
        INSERT INTO capturas_fuente(loteria_clave,fecha,fuente,resultado_json,estado,detalle)
        VALUES(?,?,?,?,?,?)
        ''',(clave,fecha,fuente,json.dumps(resultado,ensure_ascii=False) if resultado else None,estado,detalle))

def guardar_verificado(pais, clave, nombre, tipo, fecha, resultado, estado, fuentes):
    if estado not in ("OFICIAL","VERIFICADO"):
        return False
    with conectar() as conn:
        conn.execute('''
        INSERT INTO resultados_verificados
        (pais,loteria_clave,loteria_nombre,tipo_juego,fecha,resultado_json,estado,fuentes_json)
        VALUES(?,?,?,?,?,?,?,?)
        ON CONFLICT(loteria_clave,fecha) DO UPDATE SET
          resultado_json=excluded.resultado_json,
          estado=excluded.estado,
          fuentes_json=excluded.fuentes_json
        ''',(pais,clave,nombre,tipo,fecha,json.dumps(resultado,ensure_ascii=False),estado,json.dumps(fuentes,ensure_ascii=False)))
    return True

def obtener_resultados(clave, limite=3000):
    with conectar() as conn:
        rows=conn.execute('''
        SELECT * FROM resultados_verificados
        WHERE loteria_clave=?
        ORDER BY fecha DESC,id DESC LIMIT ?
        ''',(clave,limite)).fetchall()
    out=[]
    for r in rows:
        d=dict(r)
        d["resultado"]=json.loads(d.pop("resultado_json"))
        d["fuentes"]=json.loads(d.pop("fuentes_json"))
        out.append(d)
    return out

def contar(clave=None):
    with conectar() as conn:
        if clave:
            return conn.execute("SELECT COUNT(*) FROM resultados_verificados WHERE loteria_clave=?",(clave,)).fetchone()[0]
        return conn.execute("SELECT COUNT(*) FROM resultados_verificados").fetchone()[0]

def guardar_prediccion_congelada(fecha, corte, clave, ranking, metadata):
    with conectar() as conn:
        conn.execute('''
        INSERT OR IGNORE INTO predicciones_congeladas
        (fecha_operativa,corte,loteria_clave,ranking_json,metadata_json)
        VALUES(?,?,?,?,?)
        ''',(fecha,corte,clave,json.dumps(ranking,ensure_ascii=False),json.dumps(metadata,ensure_ascii=False)))
        row=conn.execute('''
        SELECT * FROM predicciones_congeladas
        WHERE fecha_operativa=? AND corte=? AND loteria_clave=?
        ''',(fecha,corte,clave)).fetchone()
    return dict(row) if row else None

def obtener_prediccion(fecha, corte, clave):
    with conectar() as conn:
        row=conn.execute('''
        SELECT * FROM predicciones_congeladas
        WHERE fecha_operativa=? AND corte=? AND loteria_clave=?
        ''',(fecha,corte,clave)).fetchone()
    if not row:
        return None
    d=dict(row)
    d["ranking"]=json.loads(d.pop("ranking_json"))
    d["metadata"]=json.loads(d.pop("metadata_json") or "{}")
    return d

def listar_predicciones_fecha(fecha):
    with conectar() as conn:
        rows=conn.execute('''
        SELECT * FROM predicciones_congeladas
        WHERE fecha_operativa=?
        ORDER BY creado_en ASC
        ''',(fecha,)).fetchall()
    out=[]
    for r in rows:
        d=dict(r)
        d["ranking"]=json.loads(d.pop("ranking_json"))
        d["metadata"]=json.loads(d.pop("metadata_json") or "{}")
        out.append(d)
    return out
