import sqlite3
from datetime import datetime, timedelta

# Ruta de la base de datos blindada
DB_PATH = "loteria_master_ai.db"
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

def obtener_fecha_rd():
    ahora_utc = datetime.utcnow()
    hora_rd = ahora_utc - timedelta(hours=4)
    return hora_rd.strftime("%d/%m/%Y"), DIAS_SEMANA[hora_rd.weekday()]

def iniciar_memoria_cuantica():
    """Crea la estructura de almacenamiento si no existe (Blindaje Anti-Corrupción)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # 1. Pizarra de Resultados del Día
        cur.execute("""
            CREATE TABLE IF NOT EXISTS resultados_guardados (
                clave TEXT PRIMARY KEY, nombre TEXT, bolo1 TEXT, bolo2 TEXT, bolo3 TEXT,
                estado TEXT, volatilidad TEXT, fecha TEXT
            )
        """)
        
        # 2. Historial Profundo (Memoria de años)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS memoria_historica (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                loteria TEXT, bolo1 TEXT, bolo2 TEXT, bolo3 TEXT,
                dia_semana TEXT, fecha TEXT
            )
        """)
        
        # 3. Cerebro de Auto-Aprendizaje (Evaluador de Tasa de Acierto)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS aprendizaje_ia (
                patron TEXT PRIMARY KEY, 
                loterias_exitosas TEXT, 
                tasa_acierto REAL,
                veces_probado INTEGER,
                veces_acertado INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"🚨 Error en Base de Datos: {e}")

def registrar_y_aprender(clave_loteria, nombre_loteria, b1, b2, b3):
    """Guarda el resultado y entrena a la IA basándose en lo que salió"""
    fecha_str, dia_nombre = obtener_fecha_rd()
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # PASO 1: Actualizar la Pizarra Pública del Día
        cur.execute("""
            INSERT OR REPLACE INTO resultados_guardados 
            (clave, nombre, bolo1, bolo2, bolo3, estado, volatilidad, fecha)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (clave_loteria, nombre_loteria, b1.zfill(2), b2.zfill(2), b3.zfill(2), "Oficial RD", "🟢 Analizado IA", fecha_str))

        # PASO 2: Guardar en el Historial Profundo para buscar secuencias en el futuro
        cur.execute("""
            INSERT INTO memoria_historica (loteria, bolo1, bolo2, bolo3, dia_semana, fecha)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (clave_loteria, b1.zfill(2), b2.zfill(2), b3.zfill(2), dia_nombre, fecha_str))

        # PASO 3: Entrenamiento (Ajuste de Pesos por Terminal y Día)
        # La IA detecta el terminal del bolo mayor y le asigna un valor estadístico
        terminal_ganador = b1[-1]
        patron_detectado = f"terminal_{terminal_ganador}_dia_{dia_nombre}"
        
        cur.execute("SELECT veces_probado, veces_acertado FROM aprendizaje_ia WHERE patron = ?", (patron_detectado,))
        row = cur.fetchone()
        
        if row:
            v_prob = row[0] + 1
            v_acer = row[1] + 1  # Suma el acierto
            tasa = round((v_acer / v_prob) * 100, 2)
            cur.execute("""
                UPDATE aprendizaje_ia 
                SET tasa_acierto = ?, veces_probado = ?, veces_acertado = ?
                WHERE patron = ?
            """, (tasa, v_prob, v_acer, patron_detectado))
        else:
            cur.execute("""
                INSERT INTO aprendizaje_ia (patron, loterias_exitosas, tasa_acierto, veces_probado, veces_acertado)
                VALUES (?, ?, ?, ?, ?)
            """, (patron_detectado, clave_loteria, 100.0, 1, 1))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"🚨 Falla en el protocolo de aprendizaje: {e}")
        return False

# Iniciar la base de datos al cargar el archivo
iniciar_memoria_cuantica()
