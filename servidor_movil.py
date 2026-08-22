import json
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn

# Importamos los dos motores maestros que acabamos de crear
import enjambre_loteria_ai
import entrenador_cuantico_ia

app = FastAPI(title="Shneyder IA Pro RD - Enjambre Cuántico Definitivo v100.0")

@app.post("/api/guardar_manual")
def guardar_manual(loteria: str = Form(...), b1: str = Form(...), b2: str = Form(...), b3: str = Form(...)):
    """Recoge el resultado de la banca y lo pasa al Entrenador Cuántico para que aprenda"""
    nombre_lot = loteria.replace("_", " ").title()
    entrenador_cuantico_ia.registrar_y_aprender(loteria, nombre_lot, b1, b2, b3)
    return RedirectResponse(url="/", status_code=303)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    # Obtenemos la hora y los cálculos directamente del Cerebro Matemático
    hora_rd, fecha_str, dia_nombre = enjambre_loteria_ai.obtener_fechas_rd()
    datos_loterias = enjambre_loteria_ai.calcular_enjambre_ia()

    # Cargar premios guardados del día si existen
    pizarra_inicial = {k: {"nombre": v["nombre"], "premios": ["--", "--", "--"], "estado": "Pendiente", "volatilidad": "🟢 Activo"} for k, v in datos_loterias.items()}
    try:
        import sqlite3
        conn = sqlite3.connect(entrenador_cuantico_ia.DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT clave, nombre, bolo1, bolo2, bolo3, estado, volatilidad FROM resultados_guardados WHERE fecha = ?", (fecha_str,))
        for f in cur.fetchall():
            c_key, nom, b1, b2, b3, st, vol = f
            if c_key in pizarra_inicial:
                pizarra_inicial[c_key] = {"nombre": nom, "premios": [b1, b2, b3], "estado": st, "volatilidad": vol}
        conn.close()
    except Exception:
        pass

    datos_json = json.dumps(datos_loterias)

    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Shneyder IA Pro RD v100.0</title>
        <style>
            * { box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #080d1a; color: #e2e8f0; margin: 0; padding: 10px; }
            .main-wrapper { max-width: 900px; margin: 0 auto; }
            .brand { display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 12px; padding: 12px 16px; margin-bottom: 12px; border: 1px solid #38bdf8; }
            .brand-left h1 { font-size: 20px; color: #38bdf8; margin: 0; font-weight: 900; }
            .brand-left p { font-size: 10px; color: #94a3b8; margin: 3px 0 0 0; text-transform: uppercase; }
            .brand-clock { font-size: 15px; color: #facc15; font-weight: 900; font-family: monospace; }
            .banca-panel { background: linear-gradient(135deg, #064e3b, #022c22); border: 2px solid #22c55e; border-radius: 12px; padding: 12px; margin-bottom: 12px; }
            .banca-form { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; gap: 6px; margin-top: 8px; }
            .banca-input, .banca-select { background: #0f172a; border: 1px solid #22c55e; color: #fff; padding: 6px; border-radius: 6px; font-size: 12px; }
            .banca-btn { background: #22c55e; color: #000; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; }
            .sniper-card { background: linear-gradient(135deg, #1e1b4b, #0f172a); border: 2px solid #818cf8; border-radius: 12px; padding: 14px; margin-bottom: 12px; }
            .sniper-grid { display: flex; justify-content: space-around; align-items: center; text-align: center; margin-bottom: 10px; }
            .sniper-item b { font-size: 10px; color: #a5b4fc; text-transform: uppercase; display: block; }
            .sniper-num { font-size: 26px; font-weight: 900; color: #38bdf8; }
            .sniper-badge { font-size: 13px; font-weight: bold; color: #4ade80; }
            .sniper-lot-box { background: rgba(15, 23, 42, 0.8); border: 1px solid #38bdf8; border-radius: 8px; padding: 6px 10px; text-align: center; font-size: 12px; }
            .tabs-scroll { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 8px; margin-bottom: 12px; -webkit-overflow-scrolling: touch; }
            .tab-btn { white-space: nowrap; background: #1f2937; color: #9ca3af; border: 1px solid #374151; padding: 6px 12px; border-radius: 16px; font-size: 11px; font-weight: bold; cursor: pointer; }
            .tab-btn.active { background: #38bdf8; color: #0f172a; border-color: #38bdf8; }
            .tab-inactiva { opacity: 0.4; text-decoration: line-through; }
            .btn-actions { display: grid; grid-template-columns: 1fr; gap: 8px; margin-bottom: 15px; }
            .btn-wa { width: 100%; background: #22c55e; color: #0f172a; font-weight: 800; text-align: center; padding: 12px; border-radius: 10px; border: none; font-size: 13px; cursor: pointer; }
            .dictamen-box { background: #0f172a; border: 1px solid #38bdf8; border-radius: 12px; padding: 12px; margin-bottom: 15px; font-size: 12px; }
            .dictamen-item { margin-bottom: 5px; display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 3px; }
            .dictamen-item b { color: #94a3b8; }
            .dictamen-val { color: #f8fafc; font-weight: bold; }
            .jugada-formada-box { background: linear-gradient(135deg, #1e1b4b, #172554); border: 2px solid #facc15; border-radius: 10px; padding: 12px; margin-top: 12px; }
            .jf-title { color: #facc15; font-size: 12px; font-weight: 900; margin-bottom: 8px; border-bottom: 1px solid rgba(250, 204, 21, 0.3); padding-bottom: 4px; }
            .jf-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-size: 12px; }
            .jf-balls { display: flex; gap: 6px; }
            .jf-ball { background: #facc15; color: #0f172a; font-weight: 900; font-size: 14px; padding: 3px 8px; border-radius: 6px; }
            .card { background: #131d31; border-radius: 12px; padding: 12px; margin-bottom: 15px; border: 1px solid #233249; }
            h2 { font-size: 14px; margin-top: 0; padding-bottom: 6px; border-bottom: 1px solid #334155; }
            table { width: 100%; border-collapse: collapse; text-align: center; font-size: 12px; }
            th { background: #1e293b; padding: 6px 2px; color: #94a3b8; font-size: 11px; }
            td { padding: 8px 3px; border-bottom: 1px solid #1e293b; }
            #toast { display: none; position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: #38bdf8; color: #0f172a; padding: 10px 20px; border-radius: 20px; font-weight: bold; font-size: 13px; z-index: 100; }
        </style>
    </head>
    <body>
        <div class="main-wrapper">
            <div class="brand">
                <div class="brand-left">
                    <h1>SHNEYDER IA PRO RD</h1>
                    <p>Enjambre Cuántico Definitivo</p>
                </div>
                <div class="brand-right">
                    <div class="brand-clock" id="live_time">--:--:--</div>
                </div>
            </div>

            <div class="banca-panel">
                <div style="color:#4ade80; font-weight:900; font-size:12px; display:flex; justify-content:space-between;">
                    <span>⚡ REGISTRO MANUAL (MODO BANCA)</span>
                    <span style="font-size:10px; color:#fff;">Entrena al Entrenador Cuántico</span>
                </div>
                <form action="/api/guardar_manual" method="POST" class="banca-form">
                    <select name="loteria" class="banca-select">
                        <option value="real">Lotería Real</option>
                        <option value="gana_mas">Gana Más</option>
                        <option value="nacional_noche">Nacional Noche</option>
                        <option value="leidsa">Leidsa</option>
                        <option value="loteka">Loteka</option>
                        <option value="primera_dia">La Primera Día</option>
                        <option value="primera_noche">La Primera Noche</option>
                        <option value="lotedom">LoteDom</option>
                    </select>
                    <input type="text" name="b1" placeholder="1ra" maxlength="2" required class="banca-input" style="text-align:center;">
                    <input type="text" name="b2" placeholder="2da" maxlength="2" required class="banca-input" style="text-align:center;">
                    <input type="text" name="b3" placeholder="3ra" maxlength="2" required class="banca-input" style="text-align:center;">
                    <button type="submit" class="banca-btn">💾 GUARDAR</button>
                </form>
            </div>

            <div class="sniper-card">
                <div class="sniper-grid">
                    <div class="sniper-item">
                        <b>🎯 TIRO DIRECTO</b>
                        <span class="sniper-num" id="s_fijo">--</span>
                    </div>
                    <div class="sniper-item">
                        <b>🛡️ REVÉS OBLIGADO</b>
                        <span class="sniper-num" style="color:#f59e0b;" id="s_virado">--</span>
                    </div>
                    <div class="sniper-item">
                        <b>💥 PALÉ TITÁN</b>
                        <span class="sniper-num" style="color:#4ade80; font-size:18px;" id="s_pale">--</span>
                    </div>
                    <div class="sniper-item">
                        <b>⚡ PROBABILIDAD</b>
                        <span class="sniper-badge" id="s_fuerza">--%</span>
                    </div>
                </div>
                <div class="sniper-lot-box">
                    <span style="color:#facc15;font-weight:900;">📍 MOTOR ACTIVO:</span>
                    <span style="color:#38bdf8;font-weight:bold;" id="s_lot_fuerte">--</span>
                </div>
            </div>

            <div class="tabs-scroll" id="contenedor_tabs"></div>

            <div class="btn-actions">
                <button class="btn-wa" onclick="copiarWhatsApp()">📋 COPIAR JUGADA PARA WHATSAPP</button>
            </div>

            <div class="dictamen-box">
                <h3>⚡ DICTAMEN DEL MOTOR <span id="dictamen_sala" style="font-size:10px;color:#94a3b8;"></span></h3>
                <div class="dictamen-item"><b>Flujo:</b> <span class="dictamen-val" id="d_flujo">--</span></div>
                <div class="dictamen-item"><b>Decena Clave:</b> <span class="dictamen-val" id="d_decena">--</span></div>
                <div class="dictamen-item"><b>Terminales:</b> <span class="dictamen-val" id="d_terminal">--</span></div>
                <div class="dictamen-item" style="border:none;"><b>Inercia:</b> <span class="dictamen-val" style="color:#38bdf8;" id="d_dia">--</span></div>

                <div class="jugada-formada-box">
                    <div class="jf-title">⚡ JUGADA FORMADA (DECENAS, TERMINALES Y JALADERAS)</div>
                    <div class="jf-row">
                        <b style="color:#a5b4fc;">🎯 3 NÚMEROS:</b>
                        <div class="jf-balls" id="jf_numeros_container"></div>
                    </div>
                    <div class="jf-row">
                        <b style="color:#a5b4fc;">💥 PALÉS:</b>
                        <span style="color:#4ade80;font-weight:900;font-size:13px;" id="jf_pales_txt">--</span>
                    </div>
                    <div class="jf-row" style="margin-bottom:0;">
                        <b style="color:#a5b4fc;">🏆 TRIPLETA:</b>
                        <span style="color:#f472b6;font-weight:900;font-size:13px;" id="jf_tripleta_txt">--</span>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2 style="color: #38bdf8;">📊 LÍNEAS ASIGNADAS POR EL MOTOR CUÁNTICO</h2>
                <table>
                    <thead><tr><th>#</th><th>NÚMERO</th><th>FUERZA</th><th>TIPO</th><th>SALA</th></tr></thead>
                    <tbody id="tabla_sueltos"></tbody>
                </table>
            </div>

            <div id="toast">¡Copiado al portapapeles! 📱</div>
        </div>

        <script>
            let db = __DATOS_JSON__;
            let tabActual = Object.keys(db)[0];

            function actualizarRelojCabecera() {
                const ahora = new Date();
                document.getElementById('live_time').innerText = 
                    String(ahora.getHours()).padStart(2, '0') + ":" + 
                    String(ahora.getMinutes()).padStart(2, '0') + ":" + 
                    String(ahora.getSeconds()).padStart(2, '0');
            }

            function construirTabs() {
                let html = "";
                for (let clave in db) {
                    let info = db[clave];
                    let claseInactiva = info.activa ? "" : " tab-inactiva";
                    let claseActiva = clave === tabActual ? " active" : "";
                    html += `<button class="tab-btn${claseActiva}${claseInactiva}" onclick="cambiarTab('${clave}')">${info.nombre.split('(')[0]}</button>`;
                }
                document.getElementById('contenedor_tabs').innerHTML = html;
            }

            function cambiarTab(clave) {
                tabActual = clave;
                construirTabs();
                actualizarVista();
            }

            function actualizarVista() {
                const info = db[tabActual] || db[Object.keys(db)[0]];
                document.getElementById('dictamen_sala').innerText = "[" + info.nombre + "]";

                if (info.tiro_fijo) {
                    document.getElementById('s_fijo').innerText = info.tiro_fijo.num;
                    document.getElementById('s_virado').innerText = info.tiro_fijo.virado;
                    document.getElementById('s_pale').innerText = info.tiro_fijo.palé_titan;
                    document.getElementById('s_fuerza').innerText = info.tiro_fijo.fuerza + "%";
                    document.getElementById('s_lot_fuerte').innerText = info.tiro_fijo.lot_fuerte;
                }

                if (info.dictamen) {
                    document.getElementById('d_flujo').innerText = info.dictamen.flujo;
                    document.getElementById('d_decena').innerText = info.dictamen.decena;
                    document.getElementById('d_terminal').innerText = info.dictamen.terminal;
                    document.getElementById('d_dia').innerText = info.dictamen.dia_tendencia;
                }

                if (info.jugada_maestra) {
                    const jm = info.jugada_maestra;
                    let htmlB = "";
                    jm.numeros_3.forEach(n => { htmlB += `<span class="jf-ball">${n}</span>`; });
                    document.getElementById('jf_numeros_container').innerHTML = htmlB;
                    document.getElementById('jf_pales_txt').innerText = `[${jm.pale_1}] / [${jm.pale_2}]`;
                    document.getElementById('jf_tripleta_txt').innerText = `[${jm.tripleta}]`;
                }

                if (info.sueltos) {
                    let htmlSueltos = "";
                    info.sueltos.forEach((item, i) => {
                        htmlSueltos += `<tr><td>#${String(i+1).padStart(2, '0')}</td><td style="color:#38bdf8;font-size:15px;font-weight:bold;">${item.num}</td><td>${item.fuerza}%</td><td>${item.tipo}</td><td>${item.lot}</td></tr>`;
                    });
                    document.getElementById('tabla_sueltos').innerHTML = htmlSueltos;
                }
            }

            function copiarWhatsApp() {
                const info = db[tabActual];
                let texto = `⚡ *SHNEYDER IA PRO RD* ⚡\\n🎯 *Sala:* ${info.nombre}\\n🎯 *Directos:* [${info.jugada_maestra.numeros_3.join(' - ')}]\\n💥 *Palés:* [${info.jugada_maestra.pale_1}]\\n🏆 *Tripleta:* [${info.jugada_maestra.tripleta}]`;
                navigator.clipboard.writeText(texto).then(() => {
                    const t = document.getElementById('toast');
                    t.style.display = 'block';
                    setTimeout(() => { t.style.display = 'none'; }, 2000);
                });
            }

            setInterval(actualizarRelojCabecera, 1000);
            actualizarRelojCabecera();
            construirTabs();
            actualizarVista();
        </script>
    </body>
    </html>
    """

    html_final = html_template.replace("__DATOS_JSON__", json.dumps(datos_loterias))
    return HTMLResponse(content=html_final)

if __name__ == "__main__":
    uvicorn.run("servidor_movil:app", host="0.0.0.0", port=10000, reload=True)
