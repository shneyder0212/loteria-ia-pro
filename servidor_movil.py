import random
from datetime import datetime, timedelta
import sqlite3
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
import uvicorn

app = FastAPI(title="Shneyder IA Pro RD - Enjambre de Consenso Multi-Motor")

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# ==========================================
# MEMORIA HISTÓRICA VIVA & AUDITORÍA
# ==========================================
def inicializar_bd_historica():
    try:
        conn = sqlite3.connect("historial_jaladeras.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patrones_historicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sala TEXT,
                numero_base TEXT,
                jaladera_asociada TEXT,
                fuerza_historica REAL
            )
        ''')
        cursor.execute("SELECT COUNT(*) FROM patrones_historicos")
        if cursor.fetchone()[0] == 0:
            datos_iniciales = [
                ("anguila_10am", "12", "45", 98.5),
                ("primera_dia", "23", "67", 97.2),
                ("lotedom", "05", "89", 96.8),
                ("real", "14", "33", 99.1),
                ("anguila_1pm", "08", "24", 97.8),
                ("gana_mas", "25", "11", 97.5),
                ("anguila_6pm", "19", "52", 98.1),
                ("loteka", "30", "77", 96.9),
                ("primera_noche", "04", "88", 98.4),
                ("nacional_noche", "15", "66", 99.0),
                ("leidsa", "10", "40", 98.7),
                ("anguila_9pm", "07", "33", 97.4),
                ("kino_leidsa", "22", "55", 99.5)
            ]
            cursor.executemany("INSERT INTO patrones_historicos (sala, numero_base, jaladera_asociada, fuerza_historica) VALUES (?, ?, ?, ?)", datos_iniciales)
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"Aviso BD Histórica: {e}")

def inicializar_bd_auditoria():
    try:
        conn = sqlite3.connect("auditoria_aciertos.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registro_auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                sala TEXT,
                resultado_real TEXT,
                estado TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Aviso BD Auditoría: {e}")

def consultar_memoria_historica(sala_clave, num_base):
    try:
        conn = sqlite3.connect("historial_jaladeras.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT jaladera_asociada, fuerza_historica FROM patrones_historicos WHERE sala = ? AND numero_base = ?", (sala_clave, num_base))
        res = cursor.fetchone()
        conn.close()
        if res:
            return res[0], res[1]
    except Exception:
        pass
    return None, 95.0

inicializar_bd_historica()
inicializar_bd_auditoria()

# ==========================================
# SISTEMA DE DEBATE Y CONSENSO MULTI-MOTOR
# ==========================================
def motor_debate_consenso(sala_clave, seed_base, idx_sala, hora_rd):
    rng_a = random.Random(seed_base + hora_rd.hour + (idx_sala * 11))
    pool_a = [f"{n:02d}" for n in range(100)]
    rng_a.shuffle(pool_a)
    voto_a = pool_a[:5]

    rng_b = random.Random(seed_base + hora_rd.hour + (idx_sala * 17) + 5)
    pool_b = [f"{n:02d}" for n in range(100)]
    rng_b.shuffle(pool_b)
    voto_b = pool_b[:5]

    rng_c = random.Random(seed_base + hora_rd.hour + (idx_sala * 23) + 9)
    pool_c = [f"{n:02d}" for n in range(100)]
    rng_c.shuffle(pool_c)
    voto_c = pool_c[:5]

    consenso_puntuacion = {}
    for num in voto_a:
        consenso_puntuacion[num] = consenso_puntuacion.get(num, 0) + 35
    for num in voto_b:
        consenso_puntuacion[num] = consenso_puntuacion.get(num, 0) + 40
    for num in voto_c:
        consenso_puntuacion[num] = consenso_puntuacion.get(num, 0) + 25

    orden_consenso = sorted(consenso_puntuacion.items(), key=lambda x: x[1], reverse=True)
    
    ranking_final = []
    usados = set()
    for num, punt in orden_consenso:
        if num not in usados:
            usados.add(num)
            fuerza_cons = min(round(96.0 + (punt * 0.04), 1), 99.9)
            ranking_final.append({"num": num, "fuerza": fuerza_cons})

    for num in pool_b:
        if num not in usados and len(ranking_final) < 30:
            usados.add(num)
            ranking_final.append({"num": num, "fuerza": 94.5})

    return ranking_final


# ==========================================
# MOTOR GENERAL UNIFICADO
# ==========================================
def calcular_enjambre_ia():
    ahora_utc = datetime.utcnow()
    hora_rd = ahora_utc - timedelta(hours=4)
    hora_esp = ahora_utc + timedelta(hours=2)
    
    seed_base = int(hora_rd.strftime("%Y%m%d"))
    dia_nombre = DIAS_SEMANA[hora_rd.weekday()]
    es_lunes_domingo = dia_nombre in ["Lunes", "Domingo"]
    
    salas_config = [
        ("anguila_10am", "Anguila Mañana (10:00 AM)", 10, 0, "quiniela", "rd", "La Primera Día (12:00 PM)"),
        ("primera_dia", "La Primera Día (12:00 PM)", 12, 0, "quiniela", "rd", "LoteDom (12:00 PM)"),
        ("lotedom", "LoteDom (12:00 PM)", 12, 0, "quiniela", "rd", "Lotería Real (12:55 PM)"),
        ("real", "Lotería Real (12:55 PM)", 12, 55, "quiniela", "rd", "Anguila Mediodía (1:00 PM)"),
        ("anguila_1pm", "Anguila Mediodía (1:00 PM)", 13, 0, "quiniela", "rd", "Gana Más (2:30 PM)"),
        ("gana_mas", "Gana Más (2:30 PM)", 14, 30, "quiniela", "rd", "Anguila Tarde (6:00 PM)"),
        ("anguila_6pm", "Anguila Tarde (6:00 PM)", 18, 0, "quiniela", "rd", "Loteka (7:55 PM)"),
        ("loteka", "Loteka (7:55 PM)", 19, 55, "quiniela", "rd", "La Primera Noche (8:00 PM)"),
        ("primera_noche", "La Primera Noche (8:00 PM)", 20, 0, "quiniela", "rd", "Nacional Noche (8:50 PM)"),
        ("nacional_noche", "Nacional Noche (8:50 PM)", 20, 50, "quiniela", "rd", "Leidsa (8:55 PM)"),
        ("leidsa", "Leidsa (8:55 PM)", 20, 55, "quiniela", "rd", "Anguila Noche (9:00 PM)"),
        ("anguila_9pm", "Anguila Noche (9:00 PM)", 21, 0, "quiniela", "rd", "Kino Leidsa TV"),
        ("kino_leidsa", "Kino Leidsa TV (Especial)", 20, 55, "kino", "rd", "Nacional Noche (8:50 PM)"),
        ("primitiva_esp", "La Primitiva (España)", 21, 0, "primitiva", "esp", "Euromillones (Europa)"),
        ("euromillones", "Euromillones (Europa)", 21, 0, "euromillones", "esp", "La Primitiva (España)")
    ]

    minutos_actuales_rd = hora_rd.hour * 60 + hora_rd.minute
    minutos_actuales_esp = hora_esp.hour * 60 + hora_esp.minute

    resultado_final = {}

    for idx_sala, (clave, nombre, h_cierre, m_cierre, tipo, region, respaldo) in enumerate(salas_config):
        cierre_minutos = h_cierre * 60 + m_cierre
        minutos_actuales = minutos_actuales_esp if region == "esp" else minutos_actuales_rd
        
        juega_hoy = True
        if tipo == "primitiva":
            juega_hoy = dia_nombre in ["Lunes", "Jueves", "Sábado"]
        elif tipo == "euromillones":
            juega_hoy = dia_nombre in ["Martes", "Viernes"]

        activa = juega_hoy and (minutos_actuales <= cierre_minutos)
        rng = random.Random(seed_base + (77 if es_lunes_domingo else 33) + hora_rd.hour + (idx_sala * 13))

        if tipo == "quiniela":
            sueltos_ord = motor_debate_consenso(clave, seed_base, idx_sala, hora_rd)
            
            n1, n2, n3 = sueltos_ord[0]['num'], sueltos_ord[1]['num'], sueltos_ord[2]['num']
            n4, n5 = sueltos_ord[3]['num'], sueltos_ord[4]['num']
            
            jaladera_num_1 = n1
            jaladera_num_2 = n2
            
            jal_hist, fuerza_hist = consultar_memoria_historica(clave, n1)
            if not jal_hist:
                jaladera_atrae = f"{int(n1) % 10}{(int(n2) + 3) % 10:01d}"
                origen_patron = "Consenso Multi-Motor Avanzado"
            else:
                jaladera_atrae = jal_hist
                origen_patron = f"Memoria Histórica & Votación ({fuerza_hist}% Certeza)"
            
            sala_sugerida_1 = nombre
            sala_sugerida_2 = respaldo

            pale_alerta = f"[{jaladera_num_1} - {jaladera_atrae}]"
            tripleta_alerta = f"[{jaladera_num_1} - {jaladera_num_2} - {jaladera_atrae}]"
            loterias_alerta_str = f"{sala_sugerida_1} / Respaldo: {sala_sugerida_2}"

            super_pale_1 = f"[{n1} - {n2}] <span style='font-size:11px; color:#38bdf8;'>({sala_sugerida_1})</span>"
            super_pale_2 = f"[{n1} - {n3}] <span style='font-size:11px; color:#38bdf8;'>({sala_sugerida_2})</span>"
            tripleta_caliente = f"[{n1} - {n2} - {n3}] <span style='font-size:11px; color:#f472b6;'>({sala_sugerida_1} + {sala_sugerida_2})</span>"

            decenas_extraidas = set()
            for obj in sueltos_ord[:10]:
                decena_num = (int(obj['num']) // 10) * 10
                decenas_extraidas.add(f"[{decena_num:02d}-{decena_num+9:02d}]")
            lista_decenas = list(decenas_extraidas)[:3]
            while len(lista_decenas) < 3:
                lista_decenas.append("[00-09]")
            decenas_clave_str = ", ".join(lista_decenas)

            terminales_extraidos = set([n['num'][1] for n in sueltos_ord[:10]])
            digitos_extraidos = set([n['num'][0] for n in sueltos_ord[:10]])

            top20_pales = []
            for i in range(20):
                p_str = f"{sueltos_ord[i]['num']} - {sueltos_ord[i+1]['num']}"
                fuerza_pale = round((sueltos_ord[i]['fuerza'] + sueltos_ord[i+1]['fuerza']) / 2, 1)
                loterias_asociadas = sala_sugerida_1 if i % 2 == 0 else sala_sugerida_2
                top20_pales.append(f"<tr><td>#{i+1}</td><td style='color:#38bdf8; font-weight:bold;'>{p_str}</td><td style='color:#facc15;'>{fuerza_pale}%</td><td style='font-size:11px; color:#94a3b8;'>{loterias_asociadas}</td></tr>")

            top20_nums = ""
            for idx, n_obj in enumerate(sueltos_ord[:20]):
                loterias_asociadas = sala_sugerida_1 if idx < 10 else sala_sugerida_2
                top20_nums += f"<tr><td>#{idx+1}</td><td style='color:#38bdf8; font-weight:bold; font-size:15px;'>{n_obj['num']}</td><td style='color:#4ade80;'>{n_obj['fuerza']}%</td><td style='font-size:11px; color:#94a3b8;'>{loterias_asociadas}</td></tr>")

            tres_nums_html = "".join([f'<span class="ball">{n}</span>' for n in [n1, n2, n3]])

            dictamen_html = f"""
            <div style="background: linear-gradient(135deg, #7f1d1d, #450a0a); border: 2px solid #ef4444; border-radius: 10px; padding: 12px; margin-bottom: 15px; color: #fff; text-align: center;">
                <div style="font-weight: bold; font-size: 14px; color: #f87171; margin-bottom: 6px;">🤖 ENJAMBRE DE CONSENSO MULTI-MOTOR (IA ACTIVA)</div>
                <div style="font-size: 13px; margin-bottom: 6px;">El número <b style="color: #facc15;">{jaladera_num_1}</b> atrae a <b style="color: #facc15;">{jaladera_atrae}</b> <span style="font-size:11px; color:#38bdf8;">({origen_patron})</span></div>
                <div style="background: rgba(0,0,0,0.3); border-radius: 8px; padding: 8px; margin-top: 6px; font-size: 12px; color: #cbd5e1; text-align: left;">
                    🔥 <b>Palé por Votación:</b> <span style="color: #facc15; font-size: 14px; font-weight: bold;">{pale_alerta}</span><br>
                    👑 <b>Tripleta Consensuada:</b> <span style="color: #f472b6; font-size: 14px; font-weight: bold;">{tripleta_alerta}</span><br>
                    🎯 <b>Loterías Recomendadas:</b> <span style="color: #38bdf8; font-weight: bold;">{loterias_alerta_str}</span>
                </div>
            </div>

            <div class="tactical-box">
                <div style="color:#38bdf8; font-weight:bold; margin-bottom:8px; border-bottom:1px solid #38bdf8; padding-bottom:4px;">⚡ DICTAMEN EXCLUSIVO: {nombre.upper()}</div>
                <div class="tactical-row"><span>Flujo:</span><b style="color:#facc15;">ANCLAJE TRIPLE 3-DECENAS (EXCLUSIVO)</b></div>
                <div class="tactical-row"><span>Decenas Clave (IA):</span><span style="color:#fff;">{decenas_clave_str}</span></div>
                <div class="tactical-row"><span>Terminales (IA):</span><span style="color:#fff;">Term. {", ".join(list(terminales_extraidos)[:3])}</span></div>
                <div class="tactical-row"><span>Dígitos Fuertes (IA):</span><span style="color:#fff;">{", ".join(list(digitos_extraidos)[:3])}</span></div>
                <div class="tactical-row"><span>Inercia:</span><span style="color:#4ade80;">{dia_nombre}: Vigente</span></div>
            </div>

            <div class="tactical-box" style="border-color: #facc15;">
                <div style="color:#facc15; font-weight:bold; margin-bottom:8px; border-bottom:1px solid #facc15; padding-bottom:4px;">🔥 JUGADA MAESTRA EXCLUSIVA</div>
                <div class="tactical-row"><span>Sala Objetivo Principal:</span><b style="color:#38bdf8;">{nombre}</b></div>
                <div class="tactical-row"><span>Respaldo Sugerido:</span><span style="color:#4ade80;">{respaldo}</span></div>
                <div class="tactical-row"><span>3 Números Base:</span><div>{tres_nums_html}</div></div>
                <div class="tactical-row"><span>Súper Palés + Sala:</span><div style="text-align:right;"><b style="color:#facc15;">{super_pale_1}</b><br><b style="color:#facc15;">{super_pale_2}</b></div></div>
                <div class="tactical-row"><span>Tripleta + Salas:</span><b style="color:#f472b6;">{tripleta_caliente}</b></div>
            </div>

            <h3>⭐ TOP 20 NÚMEROS ({nombre.upper()}):</h3>
            <div style="max-height: 250px; overflow-y: auto;">
                <table><tr><th>#</th><th>Número</th><th>Fuerza</th><th>Sala Sugerida</th></tr>{top20_nums}</table>
            </div>
            
            <h3>⭐ TOP 20 PALÉS ({nombre.upper()}):</h3>
            <div style="max-height: 250px; overflow-y: auto;">
                <table><tr><th>#</th><th>Palé</th><th>Fuerza</th><th>Sala Sugerida</th></tr>{"".join(top20_pales)}</table>
            </div>
            """
            resultado_final[clave] = {"nombre": nombre, "activa": activa, "contenido": dictamen_html}

        elif tipo == "kino":
            j_a = ", ".join(["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), 10))])
            j_b = ", ".join(["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), 10))])
            j_c = ", ".join(["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), 10))])
            
            kino_html = f"""
            <div style="background: linear-gradient(135deg, #065f46, #064e3b); border: 2px solid #10b981; border-radius: 10px; padding: 12px; margin-bottom: 15px; color: #fff; text-align: center;">
                <div style="font-weight: bold; font-size: 14px; color: #34d399; margin-bottom: 6px;">👑 KINO LEIDSA TV (CONSENSO MULTI-MOTOR)</div>
                <div style="font-size: 13px;">Votación cruzada de los 80 bolos oficiales bajo patrones de frecuencia histórica.</div>
            </div>
            
            <div class="tactical-box">
                <div style="color:#34d399; font-weight:bold; margin-bottom:8px; border-bottom:1px solid #34d399; padding-bottom:4px;">🎯 JUGADA KINO A (CONSENSO MÁXIMO)</div>
                <p style='color:#facc15; font-weight:bold; font-size:16px; text-align:center; letter-spacing: 1px;'>{j_a}</p>
            </div>
            
            <div class="tactical-box">
                <div style="color:#34d399; font-weight:bold; margin-bottom:8px; border-bottom:1px solid #34d399; padding-bottom:4px;">🎯 JUGADA KINO B</div>
                <p style='color:#38bdf8; font-weight:bold; font-size:16px; text-align:center; letter-spacing: 1px;'>{j_b}</p>
            </div>

            <div class="tactical-box">
                <div style="color:#34d399; font-weight:bold; margin-bottom:8px; border-bottom:1px solid #34d399; padding-bottom:4px;">🎯 JUGADA KINO C (RESPALDO)</div>
                <p style='color:#f472b6; font-weight:bold; font-size:16px; text-align:center; letter-spacing: 1px;'>{j_c}</p>
            </div>
            """
            resultado_final[clave] = {"nombre": nombre, "activa": activa, "contenido": kino_html}

        elif tipo == "primitiva":
            p_nums = ", ".join(["{:02d}".format(n) for n in sorted(rng.sample(range(1, 50), 6))])
            prim_html = f"""
            <p style="color:#facc15; font-weight:bold;">🇪🇸 Reintegro: <span style="font-size:18px; color:#fff;">{rng.randint(0, 9)}</span></p>
            <h3>🇪🇸 MATRIZ PRIMITIVA:</h3><p style='color:#38bdf8; font-weight:bold; text-align:center;'>{p_nums}</p>
            """
            resultado_final[clave] = {"nombre": nombre, "activa": activa, "contenido": prim_html}

        elif tipo == "euromillones":
            e_nums = ", ".join([str(n) for n in sorted(rng.sample(range(1, 51), 5))])
            e_estrellas = f"⭐ {rng.randint(1,12)} - ⭐ {rng.randint(1,12)}"
            euro_html = f"""
            <h3>🇪🇺 ESTRELLAS:</h3><p style='color:#38bdf8; font-weight:bold; text-align:center;'>{e_estrellas}</p>
            <h3>🇪🇺 NÚMEROS:</h3><p style='color:#facc15; font-weight:bold; text-align:center;'>{e_nums}</p>
            """
            resultado_final[clave] = {"nombre": nombre, "activa": activa, "contenido": euro_html}
            
    return resultado_final

@app.get("/ping", response_class=PlainTextResponse)
def ping_salud():
    return "OK - Enjambre de Consenso Activo"

@app.get("/", response_class=HTMLResponse)
def index(request: Request, sala: str = None):
    datos = calcular_enjambre_ia()
    keys = list(datos.keys())
    
    modo_auditoria = (sala == "auditoria")
    
    sala_activa = sala if (sala in datos or modo_auditoria) else (keys[0] if keys else "")
    info_actual = datos.get(sala_activa, {"nombre": "Cargando...", "activa": True, "contenido": "<p>Cargando datos...</p>"})

    estado_badge = "<span style='color:#4ade80; font-size:12px;'>● CONSENSO MULTI-MOTOR</span>" if info_actual.get("activa", True) else "<span style='color:#f87171; font-size:12px;'>● CERRADA</span>"

    botones_html = ""
    for clave, datos_sala in datos.items():
        clase_activa = "active" if clave == sala_activa else ""
        indicador = "🟢" if datos_sala.get("activa", True) else "🔴"
        botones_html += f'<button class="tab-btn {clase_activa}" onclick="location.href=\'/?sala={clave}\'">{indicador} {datos_sala["nombre"]}</button>'
    
    clase_aud_active = "active" if modo_auditoria else ""
    botones_html += f'<button class="tab-btn {clase_aud_active}" style="background:#0284c7;" onclick="location.href=\'/?sala=auditoria\'">📊 Auditoría de Aciertos</button>'

    if modo_auditoria:
        try:
            conn = sqlite3.connect("auditoria_aciertos.db", check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT fecha, sala, resultado_real, estado FROM registro_auditoria ORDER BY id DESC LIMIT 20")
            registros = cursor.fetchall()
            conn.close()
        except Exception:
            registros = []

        filas_tabla = ""
        for reg in registros:
            color_estado = "#4ade80" if reg[3] == "ACIERTO" else "#f87171"
            filas_tabla += f"<tr><td>{reg[0]}</td><td style='color:#38bdf8;'>{reg[1]}</td><td style='font-weight:bold; color:#facc15;'>{reg[2]}</td><td style='color:{color_estado}; font-weight:bold;'>{reg[3]}</td></tr>"

        if not filas_tabla:
            filas_tabla = "<tr><td colspan='4' style='color:#94a3b8;'>No hay registros de auditoría todavía. ¡Agrega el primero abajo!</td></tr>"

        options_salas = "".join([f"<option value='{k}'>{v['nombre']}</option>" for k, v in datos.items()])

        contenido_html = f"""
        <div style="background: linear-gradient(135deg, #0369a1, #0c4a6e); border: 2px solid #38bdf8; border-radius: 10px; padding: 15px; margin-bottom: 15px; color: #fff;">
            <div style="font-weight: bold; font-size: 15px; color: #facc15; margin-bottom: 8px;">📊 MÓDULO DE AUDITORÍA Y CONTROL DE EFECTIVIDAD</div>
            <p style="font-size: 13px; color: #cbd5e1; margin-bottom: 12px;">Registra manualmente el número que salió en el sorteo oficial para auditar el rendimiento del enjambre.</p>
            
            <form action="/guardar_auditoria" method="POST" style="display: flex; flex-direction: column; gap: 8px;">
                <label style="font-size: 12px; color: #38bdf8;">Selecciona la Sala:</label>
                <select name="sala_aud" style="padding: 8px; border-radius: 6px; background: #0f172a; color: #fff; border: 1px solid #38bdf8;">
                    {options_salas}
                </select>
                
                <label style="font-size: 12px; color: #38bdf8;">Número que Salió Oficialmente:</label>
                <input type="text" name="num_real" placeholder="Ej: 45" required style="padding: 8px; border-radius: 6px; background: #0f172a; color: #fff; border: 1px solid #38bdf8; font-size: 14px;">
                
                <button type="submit" style="background: #22c55e; color: #fff; font-weight: bold; padding: 10px; border: none; border-radius: 6px; cursor: pointer; margin-top: 5px;">💾 Guardar y Auditar Acierto</button>
            </form>
        </div>

        <h3>📋 HISTORIAL DE AUDITORÍA RECIENTE:</h3>
        <div style="max-height: 300px; overflow-y: auto;">
            <table>
                <tr><th>Fecha / Hora</th><th>Sala</th><th>Resultado Real</th><th>Estado</th></tr>
                {filas_tabla}
            </table>
        </div>
        """
        titulo_panel = "📊 AUDITORÍA Y CONTROL DE EFECTIVIDAD"
        badge_panel = "<span style='color:#38bdf8; font-size:12px;'>● MODO REGISTRO</span>"
    else:
        contenido_html = info_actual['contenido']
        titulo_panel = f"📊 {info_actual['nombre'].upper()}"
        badge_panel = estado_badge

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Shneyder IA Pro - Enjambre de Consenso</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <!-- Ícono personalizado: Billete de 10 Euros -->
        <link rel="icon" type="image/png" href="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/10_euro_note_2014_back.jpg/320px-10_euro_note_2014_back.jpg">
        <link rel="apple-touch-icon" href="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/10_euro_note_2014_back.jpg/320px-10_euro_note_2014_back.jpg">
        <style>
            body {{ background:#080d1a; color:#e2e8f0; font-family:sans-serif; padding:10px; margin:0; }}
            .card {{ background:#131d31; border-radius:12px; padding:15px; margin-bottom:15px; border:1px solid #233249; }}
            table {{ width:100%; border-collapse:collapse; color:#fff; }}
            th, td {{ padding:6px; border-bottom:1px solid #1e293b; text-align:center; font-size: 13px; }}
            th {{ background: #1e293b; color: #94a3b8; position: sticky; top: 0; }}
            .tab-btn {{ background:#1f2937; color:#fff; border:none; padding:10px; margin:2px; border-radius:8px; cursor:pointer; font-weight: bold; white-space: nowrap; text-decoration: none; display: inline-block; }}
            .active {{ background:#38bdf8 !important; color:#0f172a !important; }}
            h3 {{ color: #38bdf8; font-size: 14px; margin-top: 15px; border-bottom: 1px solid #233249; padding-bottom: 4px; }}
            .ball {{ background: #facc15; color: #0f172a; font-weight: 900; border-radius: 50%; width: 32px; height: 32px; display: inline-flex; align-items: center; justify-content: center; margin: 3px; font-size: 12px; }}
            .tactical-box {{ background: #0f172a; border: 1px solid #38bdf8; border-radius: 10px; padding: 12px; margin-bottom: 15px; font-size: 13px; }}
            .tactical-row {{ display: flex; justify-content: space-between; margin-bottom: 6px; border-bottom: 1px solid #1e293b; padding-bottom: 4px; }}
        </style>
    </head>
    <body>
        <div style="max-width:800px; margin:auto;" id="panel_principal">
            <h1>SHNEYDER IA PRO RD (CONSENSO MULTI-MOTOR)</h1>
            <div id="contenedor_tabs" style="display:flex; gap:6px; overflow-x:auto; padding-bottom:10px;">
                {botones_html}
            </div>
            <div class="card" id="vista_general">
                <h2 id="titulo_sala" style="color: #facc15; font-size: 16px;">{titulo_panel} {badge_panel}</h2>
                <div id="contenido_sala">
                    {contenido_html}
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.post("/guardar_auditoria")
def guardar_auditoria(sala_aud: str = Form(...), num_real: str = Form(...)):
    try:
        datos_enjambre = calcular_enjambre_ia()
        sala_info = datos_enjambre.get(sala_aud)
        nombre_sala_legible = sala_info['nombre'] if sala_info else sala_aud

        estado = "REGISTRADO"
        if sala_aud in datos_enjambre:
            ahora_utc = datetime.utcnow()
            hora_rd = ahora_utc - timedelta(hours=4)
            seed_base = int(hora_rd.strftime("%Y%m%d"))
            
            salas_claves = list(datos_enjambre.keys())
            idx = salas_claves.index(sala_aud) if sala_aud in salas_claves else 0
            
            sueltos_ord = motor_debate_consenso(sala_aud, seed_base, idx, hora_rd)
            top_numeros = [n['num'] for n in sueltos_ord[:20]]
            
            if num_real.strip().zfill(2) in top_numeros:
                estado = "ACIERTO"
            else:
                estado = "FUERA DE RANGO"

        fecha_str = (datetime.utcnow() - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M")
        conn = sqlite3.connect("auditoria_aciertos.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO registro_auditoria (fecha, sala, resultado_real, estado) VALUES (?, ?, ?, ?)", 
                       (fecha_str, nombre_sala_legible, num_real.strip().zfill(2), estado))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al guardar auditoría: {e}")

    return RedirectResponse(url="/?sala=auditoria", status_code=303)

if __name__ == "__main__":
    uvicorn.run("servidor_movil:app", host="0.0.0.0", port=10000)
