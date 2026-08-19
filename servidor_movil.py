import json
import sqlite3
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Shneyder IA Pro")
DB_PATH = "loteria_master_ai.db"

# Base de datos cuántica con todas las loterías de RD y el Caribe
DATOS_LOTERIAS = {
    "todas": {
        "nombre": "Todas las Loterías (Consenso General)",
        "salidor": "40 - 72 - 18",
        "sueltos": [
            {"num": "04", "fuerza": 98.9, "tipo": "fuerte", "lot": "Gana Mas / Nacional"},
            {"num": "40", "fuerza": 89.0, "tipo": "virado", "lot": "Gana Mas / Nacional"},
            {"num": "54", "fuerza": 76.4, "tipo": "caliente", "lot": "Leidsa 8:55pm"},
            {"num": "79", "fuerza": 71.2, "tipo": "atrasado", "lot": "Loteria Real 12:55pm"},
            {"num": "29", "fuerza": 68.5, "tipo": "fuerte", "lot": "Loteka 7:55pm"},
            {"num": "92", "fuerza": 62.1, "tipo": "caliente", "lot": "La Primera 12:00pm"},
            {"num": "15", "fuerza": 59.4, "tipo": "atrasado", "lot": "Anguila 6:00pm"},
            {"num": "63", "fuerza": 55.0, "tipo": "fuerte", "lot": "La Suerte 12:30pm"},
            {"num": "85", "fuerza": 52.3, "tipo": "fuerte", "lot": "Nacional Noche"},
            {"num": "18", "fuerza": 49.7, "tipo": "caliente", "lot": "Leidsa 8:55pm"},
            {"num": "72", "fuerza": 47.1, "tipo": "caliente", "lot": "Loteria Real 12:55pm"},
            {"num": "09", "fuerza": 44.8, "tipo": "atrasado", "lot": "La Suerte 6:00pm"},
            {"num": "23", "fuerza": 41.6, "tipo": "fuerte", "lot": "La Primera 8:00pm"},
            {"num": "50", "fuerza": 38.9, "tipo": "caliente", "lot": "Anguila 1:00pm"},
            {"num": "95", "fuerza": 36.2, "tipo": "atrasado", "lot": "LoteDom 12:00pm"},
            {"num": "17", "fuerza": 33.5, "tipo": "fuerte", "lot": "King Lottery 12:30pm"},
            {"num": "33", "fuerza": 30.1, "tipo": "fuerte", "lot": "Anguila 9:00pm"},
            {"num": "88", "fuerza": 28.4, "tipo": "caliente", "lot": "Loteria Real 12:55pm"},
            {"num": "67", "fuerza": 25.0, "tipo": "atrasado", "lot": "Loteka 7:55pm"},
            {"num": "12", "fuerza": 22.8, "tipo": "fuerte", "lot": "New York Noche"}
        ]
    },
    "nacional": {
        "nombre": "Gana Más (2:30 PM) / Nacional Noche (8:50 PM)",
        "salidor": "40 - 72 - 18",
        "sueltos": [
            {"num": "04", "fuerza": 98.9, "tipo": "fuerte", "lot": "Nacional Noche"},
            {"num": "40", "fuerza": 89.0, "tipo": "virado", "lot": "Nacional Noche"},
            {"num": "54", "fuerza": 81.3, "tipo": "caliente", "lot": "Gana Mas"},
            {"num": "79", "fuerza": 74.0, "tipo": "atrasado", "lot": "Nacional Noche"},
            {"num": "90", "fuerza": 69.5, "tipo": "fuerte", "lot": "Gana Mas"}
        ]
    },
    "leidsa": {
        "nombre": "Leidsa (8:55 PM)",
        "salidor": "29 - 92 - 15",
        "sueltos": [
            {"num": "29", "fuerza": 91.2, "tipo": "fuerte", "lot": "Leidsa"},
            {"num": "92", "fuerza": 82.0, "tipo": "virado", "lot": "Leidsa"},
            {"num": "18", "fuerza": 77.5, "tipo": "caliente", "lot": "Leidsa"},
            {"num": "63", "fuerza": 70.8, "tipo": "atrasado", "lot": "Leidsa"},
            {"num": "45", "fuerza": 66.2, "tipo": "fuerte", "lot": "Leidsa"}
        ]
    },
    "suerte_dia": {
        "nombre": "La Suerte Dominicana (12:30 PM)",
        "salidor": "72 - 09 - 23",
        "sueltos": [
            {"num": "72", "fuerza": 90.4, "tipo": "fuerte", "lot": "La Suerte Día"},
            {"num": "27", "fuerza": 81.3, "tipo": "virado", "lot": "La Suerte Día"},
            {"num": "63", "fuerza": 76.5, "tipo": "caliente", "lot": "La Suerte Día"},
            {"num": "38", "fuerza": 71.0, "tipo": "atrasado", "lot": "La Suerte Día"},
            {"num": "15", "fuerza": 65.8, "tipo": "fuerte", "lot": "La Suerte Día"}
        ]
    },
    "suerte_tarde": {
        "nombre": "La Suerte Dominicana (6:00 PM)",
        "salidor": "10 - 98 - 24",
        "sueltos": [
            {"num": "10", "fuerza": 89.2, "tipo": "fuerte", "lot": "La Suerte 6PM"},
            {"num": "01", "fuerza": 80.2, "tipo": "virado", "lot": "La Suerte 6PM"},
            {"num": "53", "fuerza": 75.8, "tipo": "caliente", "lot": "La Suerte 6PM"},
            {"num": "09", "fuerza": 70.4, "tipo": "atrasado", "lot": "La Suerte 6PM"},
            {"num": "57", "fuerza": 64.9, "tipo": "fuerte", "lot": "La Suerte 6PM"}
        ]
    },
    "anguila_6pm": {
        "nombre": "Anguila (6:00 PM)",
        "salidor": "00 - 61 - 27",
        "sueltos": [
            {"num": "31", "fuerza": 92.1, "tipo": "fuerte", "lot": "Anguila 6PM"},
            {"num": "13", "fuerza": 82.8, "tipo": "virado", "lot": "Anguila 6PM"},
            {"num": "28", "fuerza": 78.4, "tipo": "caliente", "lot": "Anguila 6PM"},
            {"num": "86", "fuerza": 72.0, "tipo": "atrasado", "lot": "Anguila 6PM"},
            {"num": "99", "fuerza": 67.5, "tipo": "fuerte", "lot": "Anguila 6PM"}
        ]
    },
    "anguila_dia_noche": {
        "nombre": "Anguila (10 AM / 1 PM / 9 PM)",
        "salidor": "98 - 71 - 80",
        "sueltos": [
            {"num": "88", "fuerza": 88.5, "tipo": "fuerte", "lot": "Anguila 1PM"},
            {"num": "15", "fuerza": 84.1, "tipo": "caliente", "lot": "Anguila 10AM"},
            {"num": "51", "fuerza": 75.6, "tipo": "virado", "lot": "Anguila 10AM"},
            {"num": "98", "fuerza": 71.3, "tipo": "atrasado", "lot": "Anguila 9PM"},
            {"num": "41", "fuerza": 66.0, "tipo": "fuerte", "lot": "Anguila 9PM"}
        ]
    },
    "real": {
        "nombre": "Lotería Real (12:55 PM)",
        "salidor": "04 - 85 - 63",
        "sueltos": [
            {"num": "85", "fuerza": 88.4, "tipo": "fuerte", "lot": "Real 12:55pm"},
            {"num": "58", "fuerza": 79.5, "tipo": "virado", "lot": "Real 12:55pm"},
            {"num": "04", "fuerza": 75.1, "tipo": "caliente", "lot": "Real 12:55pm"},
            {"num": "12", "fuerza": 71.6, "tipo": "atrasado", "lot": "Real 12:55pm"},
            {"num": "33", "fuerza": 65.0, "tipo": "fuerte", "lot": "Real 12:55pm"}
        ]
    },
    "loteka": {
        "nombre": "Loteka (7:55 PM)",
        "salidor": "79 - 54 - 40",
        "sueltos": [
            {"num": "79", "fuerza": 89.6, "tipo": "fuerte", "lot": "Loteka"},
            {"num": "97", "fuerza": 80.6, "tipo": "virado", "lot": "Loteka"},
            {"num": "50", "fuerza": 76.2, "tipo": "caliente", "lot": "Loteka"},
            {"num": "23", "fuerza": 69.8, "tipo": "atrasado", "lot": "Loteka"},
            {"num": "17", "fuerza": 64.3, "tipo": "fuerte", "lot": "Loteka"}
        ]
    },
    "primera": {
        "nombre": "La Primera (12:00 PM / 8:00 PM)",
        "salidor": "17 - 50 - 95",
        "sueltos": [
            {"num": "17", "fuerza": 86.7, "tipo": "fuerte", "lot": "La Primera"},
            {"num": "71", "fuerza": 78.0, "tipo": "virado", "lot": "La Primera"},
            {"num": "95", "fuerza": 73.4, "tipo": "caliente", "lot": "La Primera"},
            {"num": "09", "fuerza": 67.9, "tipo": "atrasado", "lot": "La Primera"},
            {"num": "88", "fuerza": 62.1, "tipo": "fuerte", "lot": "La Primera"}
        ]
    },
    "lotedom": {
        "nombre": "LoteDom / El Quemaito (12:00 PM)",
        "salidor": "16 - 37 - 45",
        "sueltos": [
            {"num": "16", "fuerza": 87.5, "tipo": "fuerte", "lot": "LoteDom"},
            {"num": "61", "fuerza": 78.7, "tipo": "virado", "lot": "LoteDom"},
            {"num": "37", "fuerza": 74.2, "tipo": "caliente", "lot": "LoteDom"},
            {"num": "45", "fuerza": 69.0, "tipo": "atrasado", "lot": "LoteDom"},
            {"num": "22", "fuerza": 63.4, "tipo": "fuerte", "lot": "LoteDom"}
        ]
    },
    "king_lottery": {
        "nombre": "King Lottery (12:30 PM / 7:30 PM)",
        "salidor": "62 - 85 - 89",
        "sueltos": [
            {"num": "62", "fuerza": 88.0, "tipo": "fuerte", "lot": "King Lottery"},
            {"num": "26", "fuerza": 79.2, "tipo": "virado", "lot": "King Lottery"},
            {"num": "35", "fuerza": 75.0, "tipo": "caliente", "lot": "King Lottery"},
            {"num": "85", "fuerza": 70.1, "tipo": "atrasado", "lot": "King Lottery"},
            {"num": "42", "fuerza": 64.7, "tipo": "fuerte", "lot": "King Lottery"}
        ]
    },
    "ny_florida": {
        "nombre": "New York & Florida",
        "salidor": "23 - 09 - 03",
        "sueltos": [
            {"num": "23", "fuerza": 87.2, "tipo": "fuerte", "lot": "NY Noche"},
            {"num": "32", "fuerza": 78.4, "tipo": "virado", "lot": "NY Noche"},
            {"num": "09", "fuerza": 74.5, "tipo": "caliente", "lot": "Florida Tarde"},
            {"num": "15", "fuerza": 68.3, "tipo": "atrasado", "lot": "NY Tarde"},
            {"num": "67", "fuerza": 61.0, "tipo": "fuerte", "lot": "Florida Noche"}
        ]
    }
}

@app.get("/", response_class=HTMLResponse)
def index():
    datos_json = json.dumps(DATOS_LOTERIAS)
    hora_actual = datetime.now().strftime("%I:%M:%S %p")

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <meta http-equiv="refresh" content="60">
        <title>Shneyder IA Pro</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #080d1a; color: #e2e8f0; margin: 0; padding: 10px; }}
            
            .brand {{ text-align: center; background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 12px; padding: 12px; margin-bottom: 10px; border: 1px solid #38bdf8; box-shadow: 0 4px 10px rgba(56,189,248,0.15); }}
            .brand h1 {{ font-size: 20px; color: #38bdf8; margin: 0; font-weight: 900; letter-spacing: 1px; }}
            .brand p {{ font-size: 11px; color: #94a3b8; margin: 3px 0 0 0; text-transform: uppercase; letter-spacing: 2px; }}
            
            .pill {{ background: #111827; padding: 10px; border-radius: 10px; text-align: center; font-size: 13px; margin-bottom: 12px; border: 1px solid #374151; }}
            
            .tabs-scroll {{ display: flex; gap: 8px; overflow-x: auto; padding-bottom: 8px; margin-bottom: 12px; -webkit-overflow-scrolling: touch; }}
            .tab-btn {{ white-space: nowrap; background: #1f2937; color: #9ca3af; border: 1px solid #374151; padding: 8px 14px; border-radius: 20px; font-size: 12px; font-weight: bold; cursor: pointer; }}
            .tab-btn.active {{ background: #38bdf8; color: #0f172a; border-color: #38bdf8; }}

            .btn-wa {{ display: block; width: 100%; background: #22c55e; color: #0f172a; font-weight: 800; text-align: center; padding: 12px; border-radius: 10px; border: none; font-size: 14px; cursor: pointer; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            
            .card {{ background: #131d31; border-radius: 12px; padding: 12px; margin-bottom: 15px; border: 1px solid #233249; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            h2 {{ font-size: 14px; margin-top: 0; padding-bottom: 6px; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }}
            .table-container {{ max-height: 400px; overflow-y: auto; -webkit-overflow-scrolling: touch; }}
            table {{ width: 100%; border-collapse: collapse; text-align: center; font-size: 12px; }}
            th {{ background: #1e293b; padding: 6px 2px; color: #94a3b8; font-size: 11px; position: sticky; top: 0; }}
            td {{ padding: 8px 3px; border-bottom: 1px solid #1e293b; }}
            
            #toast {{ display: none; position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: #38bdf8; color: #0f172a; padding: 10px 20px; border-radius: 20px; font-weight: bold; font-size: 13px; z-index: 100; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }}
        </style>
    </head>
    <body>
        <div class="brand">
            <h1>🇩🇴 SHNEYDER IA PRO</h1>
            <p>Sistema Cuántico de Loterías</p>
        </div>

        <div class="pill">
            🎯 <b>ÚLTIMO REGISTRO:</b> <span id="salidor_txt">40 - 72 - 18</span><br>
            🕒 <small>Hora: {hora_actual}</small>
        </div>

        <div class="tabs-scroll">
            <button class="tab-btn active" onclick="cambiarTab('todas')">🌐 TODAS</button>
            <button class="tab-btn" onclick="cambiarTab('nacional')">🇩🇴 NACIONAL / GANA MÁS</button>
            <button class="tab-btn" onclick="cambiarTab('leidsa')">🔵 LEIDSA</button>
            <button class="tab-btn" onclick="cambiarTab('suerte_dia')">🍀 LA SUERTE DÍA (12:30)</button>
            <button class="tab-btn" onclick="cambiarTab('suerte_tarde')">🍀 LA SUERTE 6PM</button>
            <button class="tab-btn" onclick="cambiarTab('anguila_6pm')">🇦🇮 ANGUILA 6PM</button>
            <button class="tab-btn" onclick="cambiarTab('anguila_dia_noche')">🇦🇮 ANGUILA (10AM / 1PM / 9PM)</button>
            <button class="tab-btn" onclick="cambiarTab('real')">👑 REAL</button>
            <button class="tab-btn" onclick="cambiarTab('loteka')">🔴 LOTEKA</button>
            <button class="tab-btn" onclick="cambiarTab('primera')">⭐ LA PRIMERA</button>
            <button class="tab-btn" onclick="cambiarTab('lotedom')">🔶 LOTEDOM</button>
            <button class="tab-btn" onclick="cambiarTab('king_lottery')">👑 KING LOTTERY</button>
            <button class="tab-btn" onclick="cambiarTab('ny_florida')">🗽 NEW YORK / FL</button>
        </div>

        <button class="btn-wa" onclick="copiarWhatsApp()">📋 COPIAR JUGADA PARA WHATSAPP</button>

        <div class="card" style="border: 1px solid #22c55e;">
            <h2 style="color: #4ade80;">⭐ TOP 5 LÍNEAS ÉLITE <span id="nombre_sala" style="font-size:11px;color:#94a3b8;"></span></h2>
            <table>
                <thead><tr><th>#</th><th>NÚMERO</th><th>FUERZA</th><th>ESTADO</th><th>SALA</th></tr></thead>
                <tbody id="tabla_top5"></tbody>
            </table>
        </div>

        <div class="card">
            <h2 style="color: #38bdf8;">📊 TOP 20 NÚMEROS SUELTOS</h2>
            <div class="table-container">
                <table>
                    <thead><tr><th>#</th><th>NÚMERO</th><th>FUERZA</th><th>ESTADO</th><th>SALA</th></tr></thead>
                    <tbody id="tabla_sueltos"></tbody>
                </table>
            </div>
        </div>

        <div class="card">
            <h2 style="color: #facc15;">🎯 PALÉS RECOMENDADOS</h2>
            <div class="table-container">
                <table>
                    <thead><tr><th>#</th><th>PALÉ</th><th>FUERZA</th><th>SALA</th></tr></thead>
                    <tbody id="tabla_pales"></tbody>
                </table>
            </div>
        </div>

        <div class="card">
            <h2 style="color: #f472b6;">🏆 TRIPLETAS BLINDADAS</h2>
            <div class="table-container">
                <table>
                    <thead><tr><th>#</th><th>TRIPLETA</th><th>FUERZA</th><th>SALA</th></tr></thead>
                    <tbody id="tabla_tripletas"></tbody>
                </table>
            </div>
        </div>

        <div id="toast">¡Copiado para WhatsApp! 📱</div>

        <script>
            const db = {datos_json};
            let tabActual = 'todas';

            function renderBadge(tipo) {{
                if (tipo === "virado") return "<span style='background:#f59e0b;color:#000;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>🛡️ VIRADO</span>";
                if (tipo === "caliente") return "<span style='background:#ef4444;color:#fff;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>🔥 RACHA</span>";
                if (tipo === "atrasado") return "<span style='background:#8b5cf6;color:#fff;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>⏳ ATRASADO</span>";
                return "<span style='background:#22c55e;color:#000;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>⭐ ÉLITE</span>";
            }}

            function cambiarTab(clave) {{
                tabActual = clave;
                document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');
                actualizarVista();
            }}

            function actualizarVista() {{
                const info = db[tabActual];
                document.getElementById('salidor_txt').innerText = info.salidor;
                document.getElementById('nombre_sala').innerText = "(" + info.nombre + ")";

                const sueltos = info.sueltos;
                
                // Top 5
                let htmlTop5 = "";
                sueltos.slice(0, 5).forEach((item, i) => {{
                    htmlTop5 += `<tr style="background:rgba(34,197,94,0.12);">
                        <td>#${{i+1}}</td>
                        <td style="color:#4ade80;font-size:18px;font-weight:bold;">${{item.num}}</td>
                        <td style="font-weight:bold;">${{item.fuerza}}%</td>
                        <td>${{renderBadge(item.tipo)}}</td>
                        <td style="font-size:10px;">${{item.lot}}</td>
                    </tr>`;
                }});
                document.getElementById('tabla_top5').innerHTML = htmlTop5;

                // Sueltos
                let htmlSueltos = "";
                sueltos.forEach((item, i) => {{
                    htmlSueltos += `<tr>
                        <td>#${{String(i+1).padStart(2, '0')}}</td>
                        <td style="color:#38bdf8;font-size:16px;font-weight:bold;">${{item.num}}</td>
                        <td>${{item.fuerza}}%</td>
                        <td>${{renderBadge(item.tipo)}}</td>
                        <td style="font-size:10px;">${{item.lot}}</td>
                    </tr>`;
                }});
                document.getElementById('tabla_sueltos').innerHTML = htmlSueltos;

                // Palés
                let htmlPales = "";
                let countP = 1;
                for (let i = 0; i < Math.min(sueltos.length, 6); i++) {{
                    for (let j = i + 1; j < Math.min(sueltos.length, 6); j++) {{
                        let f = ((sueltos[i].fuerza + sueltos[j].fuerza) / 2).toFixed(1);
                        htmlPales += `<tr>
                            <td>${{String(countP).padStart(2, '0')}}</td>
                            <td style="color:#facc15;font-weight:bold;font-size:15px;">${{sueltos[i].num}} - ${{sueltos[j].num}}</td>
                            <td style="font-weight:bold;color:#e2e8f0;">${{f}}%</td>
                            <td style="font-size:10px;">${{sueltos[i].lot}}</td>
                        </tr>`;
                        countP++;
                        if (countP > 20) break;
                    }}
                }}
                document.getElementById('tabla_pales').innerHTML = htmlPales;

                // Tripletas con Porcentaje de Fuerza
                let htmlTrip = "";
                let countT = 1;
                for (let i = 0; i < Math.min(sueltos.length, 5); i++) {{
                    for (let j = i + 1; j < Math.min(sueltos.length, 5); j++) {{
                        for (let k = j + 1; k < Math.min(sueltos.length, 5); k++) {{
                            let fTrip = ((sueltos[i].fuerza + sueltos[j].fuerza + sueltos[k].fuerza) / 3).toFixed(1);
                            htmlTrip += `<tr>
                                <td>${{String(countT).padStart(2, '0')}}</td>
                                <td style="color:#f472b6;font-weight:bold;font-size:14px;">${{sueltos[i].num}} - ${{sueltos[j].num}} - ${{sueltos[k].num}}</td>
                                <td style="font-weight:bold;color:#e2e8f0;">${{fTrip}}%</td>
                                <td style="font-size:10px;">${{sueltos[i].lot}}</td>
                            </tr>`;
                            countT++;
                        }}
                    }}
                }}
                document.getElementById('tabla_tripletas').innerHTML = htmlTrip || "<tr><td colspan='4'>Añadiendo datos...</td></tr>";
            }}

            function copiarWhatsApp() {{
                const info = db[tabActual];
                const topNums = info.sueltos.slice(0, 5).map(s => s.num).join(", ");
                const p1 = info.sueltos[0].num + " - " + info.sueltos[1].num;
                const p2 = info.sueltos[0].num + " - " + (info.sueltos[2] ? info.sueltos[2].num : "00");
                const trip = info.sueltos
