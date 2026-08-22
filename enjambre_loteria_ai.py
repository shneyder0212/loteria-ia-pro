import random
from datetime import datetime, timedelta

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

def obtener_tiempos():
    ahora_utc = datetime.utcnow()
    # Hora exacta en República Dominicana (UTC-4)
    hora_rd = ahora_utc - timedelta(hours=4)
    # Hora exacta en España Peninsular (UTC+2 en verano / UTC+1 en invierno, usamos UTC+2 para agosto)
    hora_esp = ahora_utc + timedelta(hours=2)
    return hora_rd, hora_esp, hora_rd.strftime("%d/%m/%Y"), DIAS_SEMANA[hora_rd.weekday()]

def calcular_enjambre_ia():
    hora_rd, hora_esp, _, dia_nombre = obtener_tiempos()
    seed_base = int(hora_rd.strftime("%Y%m%d"))
    es_lunes_domingo = dia_nombre in ["Lunes", "Domingo"]
    
    rng = random.Random(seed_base + (77 if es_lunes_domingo else 33) + hora_rd.hour)

    # Definimos las salas con su región horaria ('rd' o 'esp')
    salas_config = [
        ("anguila_10am", "Anguila Mañana (10:00 AM)", 10, 0, "quiniela", "rd"),
        ("primera_dia", "La Primera Día (12:00 PM)", 12, 0, "quiniela", "rd"),
        ("lotedom", "LoteDom (12:00 PM)", 12, 0, "quiniela", "rd"),
        ("real", "Lotería Real (12:55 PM)", 12, 55, "quiniela", "rd"),
        ("anguila_1pm", "Anguila Mediodía (1:00 PM)", 13, 0, "quiniela", "rd"),
        ("gana_mas", "Gana Más (2:30 PM)", 14, 30, "quiniela", "rd"),
        ("anguila_6pm", "Anguila Tarde (6:00 PM)", 18, 0, "quiniela", "rd"),
        ("loteka", "Loteka (7:55 PM)", 19, 55, "quiniela", "rd"),
        ("primera_noche", "La Primera Noche (8:00 PM)", 20, 0, "quiniela", "rd"),
        ("nacional_noche", "Nacional Noche (8:50 PM)", 20, 50, "quiniela", "rd"),
        ("leidsa", "Leidsa (8:55 PM)", 20, 55, "quiniela", "rd"),
        ("anguila_9pm", "Anguila Noche (9:00 PM)", 21, 0, "quiniela", "rd"),
        ("kino_leidsa", "Kino Leidsa TV", 20, 55, "kino", "rd"),
        ("primitiva_esp", "La Primitiva (España)", 21, 30, "primitiva", "esp"),
        ("euromillones", "Euromillones (Europa)", 21, 30, "euromillones", "esp")
    ]

    minutos_actuales_rd = hora_rd.hour * 60 + hora_rd.minute
    minutos_actuales_esp = hora_esp.hour * 60 + hora_esp.minute
    
    resultado_final = {}

    for clave, nombre, h_cierre, m_cierre, tipo, region in salas_config:
        cierre_minutos = h_cierre * 60 + m_cierre
        minutos_actuales = minutos_actuales_esp if region == "esp" else minutos_actuales_rd
        
        # Filtro estricto: Si ya pasó la hora de cierre en su respectivo país, omitimos la sala o la marcamos cerrada
        activa = (minutos_actuales <= cierre_minutos)
        
        # Si la lotería ya pasó hace más de 30 minutos, la filtramos por completo para que no aparezca fuera de hora
        if minutos_actuales > (cierre_minutos + 30):
            continue

        if tipo == "quiniela":
            pool_numeros = [f"{n:02d}" for n in range(100)]
            rng.shuffle(pool_numeros)
            
            sueltos = []
            for i in range(25):
                fuerza_val = round(99.9 - (i * 0.4), 1)
                sueltos.append({"num": pool_numeros[i], "fuerza": fuerza_val, "tipo": "Algoritmo Cuántico"})
            
            sueltos_ord = sorted(sueltos, key=lambda x: x['fuerza'], reverse=True)
            
            top5_pales_con_fuerza = []
            for i in range(5):
                p_str = f"{sueltos_ord[i]['num']} - {sueltos_ord[i+1]['num']}"
                fuerza_pale = round((sueltos_ord[i]['fuerza'] + sueltos_ord[i+1]['fuerza']) / 2, 1)
                top5_pales_con_fuerza.append({"pale": p_str, "fuerza": fuerza_pale})

            tripleta_str = f"{sueltos_ord[0]['num']}-{sueltos_ord[1]['num']}-{sueltos_ord[2]['num']}"

            resultado_final[clave] = {
                "nombre": nombre, "activa": activa, "tipo_juego": "quiniela",
                "rankings": {
                    "top5_nums": sueltos_ord[:5],
                    "top5_pales": top5_pales_con_fuerza,
                    "top5_tripletas": [tripleta_str],
                    "top20": sueltos_ord[:20]
                }
            }
        elif tipo == "kino":
            jugada_a = ["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), 10))]
            jugada_b = ["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), 10))]
            resultado_final[clave] = {
                "nombre": nombre, "activa": activa, "tipo_juego": "kino",
                "kino_data": {"jugada_a": jugada_a, "jugada_b": jugada_b}
            }
        elif tipo == "primitiva":
            prim_base = ["{:02d}".format(n) for n in sorted(rng.sample(range(1, 50), 6))]
            resultado_final[clave] = {
                "nombre": nombre, "activa": activa, "tipo_juego": "primitiva",
                "primitiva_data": {"reintegro": str(rng.randint(0, 9)), "numeros_base": prim_base}
            }
        elif tipo == "euromillones":
            euro_nums = sorted(rng.sample(range(1, 51), 5))
            e1, e2 = "{:02d}".format(rng.randint(1, 12)), "{:02d}".format(rng.randint(1, 12))
            resultado_final[clave] = {
                "nombre": nombre, "activa": activa, "tipo_juego": "euromillones",
                "euro_data": {"estrellas": [e1, e2], "numeros": euro_nums}
            }
            
    return resultado_final
