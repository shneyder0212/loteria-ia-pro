import os, sqlite3, json
from contextlib import contextmanager

DB_PATH = os.getenv('DB_PATH','loteria_master_ai.db')
os.makedirs(os.path.dirname(DB_PATH) or '.', exist_ok=True)

@contextmanager
def conectar():
    conn=sqlite3.connect(DB_PATH,timeout=30)
    conn.row_factory=sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def inicializar_db():
    with conectar() as conn:
        c=conn.cursor(); c.execute('PRAGMA journal_mode=WAL')
        c.execute('''CREATE TABLE IF NOT EXISTS resultados_verificados(id INTEGER PRIMARY KEY AUTOINCREMENT,pais TEXT NOT NULL,loteria_clave TEXT NOT NULL,loteria_nombre TEXT NOT NULL,tipo_juego TEXT NOT NULL,fecha TEXT NOT NULL,resultado_json TEXT NOT NULL,estado TEXT NOT NULL,fuentes_json TEXT NOT NULL,creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,UNIQUE(loteria_clave,fecha))''')
        c.execute('''CREATE TABLE IF NOT EXISTS resultados_observados(id INTEGER PRIMARY KEY AUTOINCREMENT,pais TEXT NOT NULL,loteria_clave TEXT NOT NULL,loteria_nombre TEXT NOT NULL,tipo_juego TEXT NOT NULL,fecha TEXT NOT NULL,resultado_json TEXT NOT NULL,fuente TEXT NOT NULL,fecha_fuente TEXT,creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,UNIQUE(loteria_clave,fecha,fuente))''')
        c.execute('''CREATE TABLE IF NOT EXISTS capturas_fuente(id INTEGER PRIMARY KEY AUTOINCREMENT,loteria_clave TEXT NOT NULL,fecha_objetivo TEXT NOT NULL,fecha_fuente TEXT,fuente TEXT NOT NULL,resultado_json TEXT,estado TEXT NOT NULL,detalle TEXT,creado_en DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS predicciones_congeladas(id INTEGER PRIMARY KEY AUTOINCREMENT,fecha_operativa TEXT NOT NULL,corte TEXT NOT NULL,loteria_clave TEXT NOT NULL,ranking_json TEXT NOT NULL,metadata_json TEXT,creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,UNIQUE(fecha_operativa,corte,loteria_clave))''')
        c.execute('''CREATE TABLE IF NOT EXISTS evaluaciones(id INTEGER PRIMARY KEY AUTOINCREMENT,fecha_operativa TEXT NOT NULL,corte TEXT NOT NULL,loteria_clave TEXT NOT NULL,aciertos_top5 INTEGER DEFAULT 0,aciertos_top10 INTEGER DEFAULT 0,aciertos_top20 INTEGER DEFAULT 0,acertados_json TEXT,creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,UNIQUE(fecha_operativa,corte,loteria_clave))''')
        c.execute('''CREATE TABLE IF NOT EXISTS estado_sistema(clave TEXT PRIMARY KEY,valor TEXT,actualizado_en DATETIME DEFAULT CURRENT_TIMESTAMP)''')

def guardar_estado(clave,valor):
    if not isinstance(valor,str): valor=json.dumps(valor,ensure_ascii=False)
    with conectar() as conn:
        conn.execute('''INSERT INTO estado_sistema(clave,valor,actualizado_en) VALUES(?,?,CURRENT_TIMESTAMP) ON CONFLICT(clave) DO UPDATE SET valor=excluded.valor,actualizado_en=CURRENT_TIMESTAMP''',(clave,valor))

def leer_estado(clave):
    with conectar() as conn:
        r=conn.execute('SELECT valor,actualizado_en FROM estado_sistema WHERE clave=?',(clave,)).fetchone()
    return dict(r) if r else None

def guardar_captura(clave,fecha_objetivo,fecha_fuente,fuente,resultado,estado,detalle=''):
    with conectar() as conn:
        conn.execute('''INSERT INTO capturas_fuente(loteria_clave,fecha_objetivo,fecha_fuente,fuente,resultado_json,estado,detalle) VALUES(?,?,?,?,?,?,?)''',(clave,fecha_objetivo,fecha_fuente,fuente,json.dumps(resultado,ensure_ascii=False) if resultado else None,estado,detalle))

def guardar_verificado(pais,clave,nombre,tipo,fecha,resultado,estado,fuentes):
    if estado not in ('OFICIAL','VERIFICADO'): return False
    with conectar() as conn:
        conn.execute('''INSERT INTO resultados_verificados(pais,loteria_clave,loteria_nombre,tipo_juego,fecha,resultado_json,estado,fuentes_json) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(loteria_clave,fecha) DO UPDATE SET resultado_json=excluded.resultado_json,estado=excluded.estado,fuentes_json=excluded.fuentes_json''',(pais,clave,nombre,tipo,fecha,json.dumps(resultado,ensure_ascii=False),estado,json.dumps(fuentes,ensure_ascii=False)))
    return True

def obtener_resultados(clave,limite=3000):
    with conectar() as conn:
        rows=conn.execute('SELECT * FROM resultados_verificados WHERE loteria_clave=? ORDER BY fecha DESC,id DESC LIMIT ?',(clave,limite)).fetchall()
    out=[]
    for r in rows:
        d=dict(r); d['resultado']=json.loads(d.pop('resultado_json')); d['fuentes']=json.loads(d.pop('fuentes_json')); out.append(d)
    return out

def ultimo_resultado(clave):
    r=obtener_resultados(clave,1); return r[0] if r else None

def contar(clave=None):
    with conectar() as conn:
        if clave: return conn.execute('SELECT COUNT(*) FROM resultados_verificados WHERE loteria_clave=?',(clave,)).fetchone()[0]
        return conn.execute('SELECT COUNT(*) FROM resultados_verificados').fetchone()[0]

def guardar_prediccion_congelada(fecha,corte,clave,ranking,metadata):
    with conectar() as conn:
        conn.execute('INSERT OR IGNORE INTO predicciones_congeladas(fecha_operativa,corte,loteria_clave,ranking_json,metadata_json) VALUES(?,?,?,?,?)',(fecha,corte,clave,json.dumps(ranking,ensure_ascii=False),json.dumps(metadata,ensure_ascii=False)))
    return obtener_prediccion(fecha,corte,clave)

def obtener_prediccion(fecha,corte,clave):
    with conectar() as conn:
        row=conn.execute('SELECT * FROM predicciones_congeladas WHERE fecha_operativa=? AND corte=? AND loteria_clave=?',(fecha,corte,clave)).fetchone()
    if not row: return None
    d=dict(row); d['ranking']=json.loads(d.pop('ranking_json')); d['metadata']=json.loads(d.pop('metadata_json') or '{}'); return d

def listar_predicciones_fecha(fecha):
    with conectar() as conn:
        rows=conn.execute('SELECT * FROM predicciones_congeladas WHERE fecha_operativa=? ORDER BY creado_en ASC',(fecha,)).fetchall()
    out=[]
    for r in rows:
        d=dict(r); d['ranking']=json.loads(d.pop('ranking_json')); d['metadata']=json.loads(d.pop('metadata_json') or '{}'); out.append(d)
    return out

def guardar_evaluacion(fecha,corte,clave,a5,a10,a20,acertados):
    with conectar() as conn:
        conn.execute('''INSERT INTO evaluaciones(fecha_operativa,corte,loteria_clave,aciertos_top5,aciertos_top10,aciertos_top20,acertados_json) VALUES(?,?,?,?,?,?,?) ON CONFLICT(fecha_operativa,corte,loteria_clave) DO UPDATE SET aciertos_top5=excluded.aciertos_top5,aciertos_top10=excluded.aciertos_top10,aciertos_top20=excluded.aciertos_top20,acertados_json=excluded.acertados_json''',(fecha,corte,clave,a5,a10,a20,json.dumps(acertados,ensure_ascii=False)))

def resumen_estado(): return {'db_path':DB_PATH,'resultados_totales':contar()}


def obtener_ultimos_rd(limite=100):
    with conectar() as conn:
        rows=conn.execute('''
        SELECT * FROM resultados_verificados
        WHERE pais='rd'
        ORDER BY fecha DESC,id DESC LIMIT ?
        ''',(limite,)).fetchall()
    out=[]
    for r in rows:
        d=dict(r)
        d['resultado']=json.loads(d.pop('resultado_json'))
        d['fuentes']=json.loads(d.pop('fuentes_json'))
        out.append(d)
    return out

def obtener_evaluaciones(clave=None, limite=1000):
    with conectar() as conn:
        if clave:
            rows=conn.execute('''
            SELECT * FROM evaluaciones
            WHERE loteria_clave=?
            ORDER BY creado_en DESC LIMIT ?
            ''',(clave,limite)).fetchall()
        else:
            rows=conn.execute('''
            SELECT * FROM evaluaciones
            ORDER BY creado_en DESC LIMIT ?
            ''',(limite,)).fetchall()
    out=[]
    for r in rows:
        d=dict(r)
        try:
            d['acertados']=json.loads(d.pop('acertados_json') or '[]')
        except Exception:
            d['acertados']=[]
        out.append(d)
    return out


def capturas_validas(clave, fecha):
    with conectar() as conn:
        rows=conn.execute('''
        SELECT * FROM capturas_fuente
        WHERE loteria_clave=? AND fecha_objetivo=? AND estado='OK'
        ORDER BY id DESC
        ''',(clave,fecha)).fetchall()
    out=[]
    for r in rows:
        d=dict(r)
        try:
            d['resultado']=json.loads(d.pop('resultado_json') or 'null')
        except Exception:
            d['resultado']=None
        out.append(d)
    return out

def reconciliar_capturas_rd(clave, fecha, nombre, tipo):
    rows=capturas_validas(clave,fecha)
    por_fuente={}
    for r in rows:
        if r.get('fecha_fuente') != fecha or not r.get('resultado'):
            continue
        por_fuente[r.get('fuente')]=r.get('resultado')
    fuentes=list(por_fuente)
    for i,a in enumerate(fuentes):
        for b in fuentes[i+1:]:
            if por_fuente[a] == por_fuente[b]:
                guardar_verificado('rd',clave,nombre,tipo,fecha,por_fuente[a],'VERIFICADO',[a,b])
                return True
    return False


def guardar_observado(pais,clave,nombre,tipo,fecha,resultado,fuente,fecha_fuente=None):
    if not resultado:
        return False
    with conectar() as conn:
        conn.execute('''
        INSERT INTO resultados_observados
        (pais,loteria_clave,loteria_nombre,tipo_juego,fecha,resultado_json,fuente,fecha_fuente)
        VALUES(?,?,?,?,?,?,?,?)
        ON CONFLICT(loteria_clave,fecha,fuente) DO UPDATE SET
          resultado_json=excluded.resultado_json,
          fecha_fuente=excluded.fecha_fuente,
          creado_en=CURRENT_TIMESTAMP
        ''',(pais,clave,nombre,tipo,fecha,json.dumps(resultado,ensure_ascii=False),fuente,fecha_fuente))
    return True

def obtener_observados(clave,limite=3000):
    with conectar() as conn:
        rows=conn.execute('''
        SELECT * FROM resultados_observados
        WHERE loteria_clave=?
        ORDER BY fecha DESC,id DESC LIMIT ?
        ''',(clave,limite)).fetchall()
    out=[]
    for r in rows:
        d=dict(r)
        d['resultado']=json.loads(d.pop('resultado_json'))
        d['calidad']='OBSERVADO'
        out.append(d)
    return out

def contar_observados(clave=None):
    with conectar() as conn:
        if clave:
            return conn.execute('SELECT COUNT(*) FROM resultados_observados WHERE loteria_clave=?',(clave,)).fetchone()[0]
        return conn.execute('SELECT COUNT(*) FROM resultados_observados').fetchone()[0]

def obtener_resultados_trabajo(clave,limite=3000):
    # Prefer verified/offical result for a date; otherwise use the newest observed source.
    ver=obtener_resultados(clave,limite)
    by_date={}
    for r in ver:
        r=dict(r)
        r['calidad']=r.get('estado','VERIFICADO')
        by_date[r['fecha']]=r

    obs=obtener_observados(clave,limite*2)
    for r in obs:
        if r['fecha'] not in by_date:
            by_date[r['fecha']]=r

    rows=list(by_date.values())
    rows.sort(key=lambda x:(x.get('fecha',''),x.get('id',0)), reverse=True)
    return rows[:limite]

def contar_trabajo(clave=None):
    if clave:
        return len(obtener_resultados_trabajo(clave,100000))
    with conectar() as conn:
        claves=[r[0] for r in conn.execute('''
        SELECT DISTINCT loteria_clave FROM resultados_verificados
        UNION
        SELECT DISTINCT loteria_clave FROM resultados_observados
        ''').fetchall()]
    return sum(len(obtener_resultados_trabajo(c,100000)) for c in claves)

def resumen_memoria_clave(clave):
    trabajo=obtener_resultados_trabajo(clave,100000)
    verificados=contar(clave)
    observados=contar_observados(clave)
    return {
        'clave':clave,
        'total_utilizable':len(trabajo),
        'verificados':verificados,
        'observados_fuente':observados,
        'calidad_ultima':trabajo[0].get('calidad') if trabajo else None,
        'fecha_ultima':trabajo[0].get('fecha') if trabajo else None,
    }
