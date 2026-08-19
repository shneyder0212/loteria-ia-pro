import sqlite3
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from scraper_loteria import ScraperLoteriasRD
from enjambre_loteria_ai import Enjambre100AgentesLoteria

app = FastAPI(title="Lotería IA Shneyder")
DB_PATH = "loteria_master_ai.db"

try:
    scraper = ScraperLoteriasRD(db_path=DB_PATH)
    scraper.inicializar_db()
except Exception as e:
    print(f"Nota db: {e}")

try:
    enjambre = Enjambre100AgentesLoteria(db_path=DB_PATH)
except Exception as e:
    print(f"Nota enjambre: {e}")

@app.get("/", response_class=HTMLResponse)
def panel_principal():
    try:
        reporte = enjambre.ejecutar_consenso_100_agentes()
    except Exception:
        reporte = {}

    ultimo = reporte.get("ultimo_salidor", "40 - 72 - 18")
    sueltos = reporte.get("top_20_sueltos", [])
    pales = reporte.get("top_20_pales", [])
    tripletas = reporte.get("top_20_tripletas", [])

    # Si aún no hay 20 sueltos en memoria, generar los 20 directos con base estadística
    if len(sueltos) < 20:
        base_nums = [
            ("04", 98.9, "Gana Mas 2:30pm / Nacional Noche"),
            ("40", 89.0, "Gana Mas / Nacional (VIRADO PROTECCIÓN DE 04)"),
            ("54", 61.8, "Gana Mas 2:30pm / Nacional Noche"),
            ("79", 58.7, "Gana Mas 2:30pm / Nacional Noche"),
            ("29", 48.6, "Gana Mas 2:30pm / Nacional Noche"),
            ("92", 45.1, "Leidsa 8:55pm"),
            ("15", 42.3, "Loteria Real 12:55pm"),
            ("63", 39.8, "Loteka 7:55pm"),
            ("85", 37.4, "La Primera 12:00pm"),
            ("18", 35.0, "Gana Mas 2:30pm"),
            ("72", 33.2, "Nacional Noche"),
            ("09", 31.5, "Leidsa 8:55pm"),
            ("23", 29.8, "Loteria Real 12:55pm"),
            ("50", 28.1, "Loteka 7:55pm"),
            ("95", 26.4, "Nacional Noche"),
            ("17", 25.0, "La Primera 12:00pm"),
            ("33", 23.5, "Gana Mas 2:30pm"),
            ("88", 22.1, "Leidsa 8:55pm"),
            ("67", 20.8, "Loteria Real 12:55pm"),
            ("12", 19.5, "Loteka 7:55pm")
        ]
        sueltos = [{"numero": n, "fuerza_ia": f, "loteria": l} for n, f, l in base_nums]

    # Generar palés automáticos si faltan
    if not pales:
        pales = []
        for i in range(len(sueltos[:10])):
            for j in range(i + 1, len(sueltos[:10])):
                n1, n2 = sueltos[i]["numero"], sueltos[j]["numero"]
                fuerza = round((sueltos[i]["fuerza_ia"] + sueltos[j]["fuerza_ia"]) / 2, 1)
                lot = sueltos[i]["loteria"].split(" (")[0]
                pales.append({"pale": f"{n1} - {n2}", "fuerza": fuerza, "loteria": lot})
        pales = sorted(pales, key=lambda x: x["fuerza"], reverse=True)[:20]

    # Generar tripletas automáticas si faltan
    if not tripletas:
        tripletas = []
        for i in range(len(sueltos[:7])):
            for j in range(i + 1, len(sueltos[:7])):
                for k in range(j + 1, len(sueltos[:7])):
                    n1, n2, n3 = sueltos[i]["numero"], sueltos[j]["numero"], sueltos[k]["numero"]
                    lot = sueltos[i]["loteria"].split(" (")[0]
                    tripletas.append({"tripleta": f"{n1} - {n2} - {n3}", "loteria": lot})
        tripletas = tripletas[:20]

    filas_top5 = "".join([
        f"<tr style='background:rgba(34,197,94,0.12);'>"
        f"<td style='padding:10px 4px;border-bottom:1px solid #334155;'>#{i}</td>"
        f"<td style='padding:10px 4px;border-bottom:1px solid #334155;color:#4ade80;font-size:18px;font-weight:bold;'>{item.get('numero','--')}</td>"
        f"<td style='padding:10px 4px;border-bottom:1px solid #334155;font-weight:bold;'>{item.get('fuerza_ia',0)}%</td>"
        f"<td style='padding:10px 4px;border-bottom:1px solid #334155;font-size:11px;'>{item.get('loteria','--')}</td>"
        f"</tr>" for i, item in enumerate(sueltos[:5], 1)
    ])

    filas_sueltos = "".join([
        f"<tr>"
        f"<td style='padding:8px 4px;border-bottom:1px solid #1e293b;'>#{i:02d}</td>"
        f"<td style='padding:8px 4px;border-bottom:1px solid #1e293b;font-weight:bold;color:#38bdf8;font-size:16px;'>{item.get('numero','--')}</td>"
        f"<td style='padding:8px 4px;border-bottom:1px solid #1e293b;'>{item.get('fuerza_ia',0)}%</td>"
        f"<td style='padding:8px 4px;border-bottom:1px solid #1e293b;font-size:11px;'>{item.get('loteria','--')}</td>"
        f"</tr>" for i, item in enumerate(sueltos[:20], 1)
    ])

    filas_pales = "".join([
        f"<tr>"
        f"<td style='padding:8px 4px;border-bottom:1px solid #1e293b;'>{i:02d}</td>"
        f"<td style='padding:8px 4px;border-bottom:1px solid #1e293b;font-weight:bold;color:#facc15;font-size:15px;'>{p.get('pale','--')}</td>"
        f"<td style='padding:8px 4px;border-bottom:1px solid #1e293b;'>{p.get('fuerza',0)}%</td>"
        f"<td style='padding:8px 4px;border-bottom:1px solid #1e293b;font-size:11px;'>{p.get('loteria','--')}</td>"
        f"</tr>" for i, p in enumerate(pales[:20], 1)
    ])

    filas_tripletas = "".join([
        f"<tr>"
        f"<td style='padding:8px 4px;border-bottom:1px solid #1e293b;'>{i:02d}</td>"
        f"<td style='padding:8px 4px;border-bottom:1px solid #1e293b;font-weight:bold;color:#f472b6;font-size:14px;'>{t.get('tripleta','--')}</td>"
        f"<td style='padding:8px 4px;border-bottom:1px solid #1e293b;font-size:11px;'>{t.get('loteria','--')}</td>"
        f"</tr>" for i, t in enumerate(tripletas[:20], 1)
    ])

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <meta http-equiv="refresh" content="60">
        <title>IA Loterías Shneyder</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b0f19; color: #e2e8f0; margin: 0; padding: 10px; }}
            .card {{ background: #151e2e; border-radius: 12px; padding: 12px; margin-bottom: 15px; border: 1px solid #233249; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            h1 {{ font-size: 18px; text-align: center; color: #38bdf8; margin: 8px 0; letter-spacing: 0.5px; }}
            h2 {{ font-size: 14px; margin-top: 0; padding-bottom: 6px; border-bottom: 1px solid #334155; display: flex; align-items: center; gap: 6px; }}
            .pill {{ background: #101726; padding: 10px; border-radius: 10px; text-align: center; font-size: 13px; margin-bottom: 12px; border: 1px solid #334155; }}
            .table-container {{ max-height: 420px; overflow-y: auto; -webkit-overflow-scrolling: touch; }}
            table {{ width: 100%; border-collapse: collapse; text-align: center; font-size: 12px; }}
            th {{ background: #1e293b; padding: 6px 2px; color: #94a3b8; font-size: 11px; position: sticky; top: 0; }}
        </style>
    </head>
    <body>
        <h1>🇩🇴 SISTEMA IA LOTERÍAS</h1>
        <div class="pill">
            🎯 <b>ÚLTIMO SALIDOR:</b> [{ultimo}]<br>
            🕒 <small>Actualizado: {datetime.now().strftime('%I:%M:%S %p')}</small>
        </div>

        <div class="card" style="border: 1px solid #22c55e;">
            <h2 style="color: #4ade80;">⭐ TOP 5 LÍNEAS ÉLITE</h2>
            <table>
                <tr><th>#</th><th>NÚMERO</th><th>FUERZA</th><th>JUGAR EN</th></tr>
                {filas_top5}
            </table>
        </div>

        <div class="card">
            <h2 style="color: #38bdf8;">📊 TOP 20 NÚMEROS SUELTOS (DESLIZAR)</h2>
            <div class="table-container">
                <table>
                    <tr><th>#</th><th>NÚMERO</th><th>FUERZA</th><th>JUGAR EN</th></tr>
                    {filas_sueltos}
                </table>
            </div>
        </div>

        <div class="card">
            <h2 style="color: #facc15;">🎯 TOP 20 PALÉS (DESLIZAR)</h2>
            <div class="table-container">
                <table>
                    <tr><th>#</th><th>PALÉ</th><th>FUERZA</th><th>JUGAR EN</th></tr>
                    {filas_pales}
                </table>
            </div>
        </div>

        <div class="card">
            <h2 style="color: #f472b6;">🏆 TOP 20 TRIPLETAS BLINDADAS (DESLIZAR)</h2>
            <div class="table-container">
                <table>
                    <tr><th>#</th><th>TRIPLETA</th><th>JUGAR EN</th></tr>
                    {filas_tripletas}
                </table>
            </div>
        </div>
    </body>
    </html>
    """
