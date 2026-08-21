import json
import sqlite3
import random
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn

app = FastAPI(title="Shneyder IA Pro RD - Titan Quantum Definitivo v70.0")
DB_PATH = "shneyder_quantum.db"

# --- [ BLOQUE DE INICIALIZACIÓN ] ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS resultados_guardados (
            clave TEXT PRIMARY KEY,
            nombre TEXT,
            bolo1 TEXT,
            bolo2 TEXT,
            bolo3 TEXT,
            estado TEXT,
            volatilidad TEXT,
            fecha TEXT
        )
    """)
    conn.commit()
    conn.close()
init_db()

# --- [ MOTOR DE ANÁLISIS INTERNACIONAL ] ---
def cluster_ia_internacional():
    rng = random.Random()
    kino_duenos = ["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), 10))]
    prim_nums = sorted(rng.sample(range(1, 50), 6))
    prim_reintegro = str(rng.randint(0, 9))
    ed_nums = sorted(rng.sample(range(1, 41), 6))
    
    return {
        "kino_leidsa": {
            "nombre": "VENTA ESPECIAL: KINO LEIDSA TV",
            "tipo_juego": "kino",
            "kino_data": {
                "duenos": kino_duenos,
                "bloques_5": [{"bloque": " - ".join(["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), 5))]), "fuerza": 98.6}],
                "bloques_7": [{"bloque": " - ".join(["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), 7))]), "fuerza": 99.1}]
            }
        },
        "primitiva_esp": {
            "nombre": "🇪🇸 LA PRIMITIVA (ESPAÑA)",
            "tipo_juego": "primitiva",
            "primitiva_data": {
                "reintegro": prim_reintegro,
                "apuestas": [{"combinacion": " - ".join(["{:02d}".format(n) for n in prim_nums])}]
            }
        },
        "eurodreams": {
            "nombre": "🇪🇺 EURODREAMS (6/40)",
            "tipo_juego": "eurodreams",
            "ed_data": {"apuestas": [{"combinacion": " - ".join(["{:02d}".format(n) for n in ed_nums])}]}
        }
    }

# --- [ PANEL DE BANCA ] ---
@app.post("/api/guardar_manual")
def guardar_manual(loteria: str = Form(...), b1: str = Form(...), b2: str = Form(...), b3: str = Form(...)):
    fecha_str = datetime.now().strftime("%d/%m/%Y")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO resultados_guardados VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                (loteria, loteria.title(), b1, b2, b3, "Manual", "🟢", fecha_str))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/", status_code=303)

# --- [ INTERFAZ PRINCIPAL ] ---
@app.get("/", response_class=HTMLResponse)
def index():
    data = cluster_ia_internacional()
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Shneyder IA Pro v70.0</title>
        <style>
            body {{ background: #080d1a; color: #fff; font-family: sans-serif; padding: 20px; }}
            .container {{ max-width: 800px; margin: auto; }}
            .panel {{ background: #131d31; padding: 20px; border-radius: 12px; border: 1px solid #38bdf8; }}
            .input-group {{ display: flex; gap: 10px; margin-top: 10px; }}
            input, button {{ padding: 12px; border-radius: 6px; border: none; width: 100%; }}
            button {{ background: #22c55e; color: black; font-weight: bold; cursor: pointer; }}
            .card {{ background: #182234; padding: 15px; border-radius: 8px; margin-top: 15px; border: 1px solid #28384e; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>SHNEYDER IA PRO - PANEL MANUAL</h1>
            <div class="panel">
                <form action="/api/guardar_manual" method="POST">
                    <input type="text" name="loteria" placeholder="Nombre del Sorteo" required style="margin-bottom:10px;">
                    <div class="input-group">
                        <input type="text" name="b1" placeholder="1ra" maxlength="2" required>
                        <input type="text" name="b2" placeholder="2da" maxlength="2" required>
                        <input type="text" name="b3" placeholder="3ra" maxlength="2" required>
                    </div>
                    <button type="submit" style="margin-top:10px;">GUARDAR RESULTADO</button>
                </form>
            </div>
            <h2>Pizarra Internacional</h2>
            <div id="pizarra_int"></div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000, reload=True)
