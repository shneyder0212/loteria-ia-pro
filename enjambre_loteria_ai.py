import random
from datetime import datetime, timedelta

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

def obtener_fechas_rd():
    ahora_utc = datetime.utcnow()
    hora_rd = ahora_utc - timedelta(hours=4)
    return hora_rd, hora_rd.strftime("%d/%m/%Y"), DIAS_SEMANA[hora_rd.weekday()]

def calcular_enjambre_ia():
    hora_rd, _, dia_nombre = obtener_fechas_rd()
    seed_base = int(hora_rd.strftime("%Y%m%d"))
    es_lunes_domingo = dia_nombre in ["Lunes", "Domingo"]
    rng = random.Random(seed_base + (77 if es_lunes_domingo else 33))

    salas_config = [
        ("real", "Lotería Real", 12, 55, "quiniela"),
        ("gana_mas", "Gana Más", 14, 30, "quiniela"),
        ("nacional_noche", "Nacional Noche", 20, 50, "quiniela"),
        ("leidsa", "Leidsa", 20, 55, "quiniela"),
        ("loteka", "Loteka", 19, 55, "quiniela"),
        ("primera_dia", "La Primera Día", 12, 0, "quiniela"),
        ("primera_noche", "La Primera Noche", 20, 0, "quiniela"),
        ("kino_leidsa", "Kino Leidsa TV", 20, 55, "kino")
    ]

    hora_actual_minutos = hora_rd.hour * 60 + hora_rd.minute
    resultado_final = {}

    for clave, nombre, h_cierre, m_cierre, tipo in salas_config:
        cierre_minutos = h_cierre * 60 + m_cierre
        activa = (hora_actual_minutos <= cierre_minutos)
        
        if tipo == "quiniela":
            decena_base = rng.choice([10, 30, 40, 70, 80])
            sueltos = []
            for i in range(25): 
                num = "{:02d}".format(decena_base + rng.randint(0, 9))
                sueltos.append({"num": num, "fuerza": round(99.9 - (i*0.4), 1), "tipo": "Algoritmo"})
            
            sueltos_ord = sorted(sueltos, key=lambda x: x['fuerza'], reverse=True)
            
            resultado_final[clave] = {
                "nombre": nombre, "activa": activa, "tipo_juego": "quiniela",
                "tiro_fijo": {"num": sueltos_ord[0]['num'], "virado": sueltos_ord[0]['num'][::-1], "fuerza": 99.6, "palé_titan": f"{sueltos_ord[0]['num']}-{sueltos_ord[1]['num']}"},
                "rankings": {
                    "top5_nums": sueltos_ord[:5],
                    "top5_pales": [f"{sueltos_ord[i]['num']}-{sueltos_ord[i+1]['num']}" for i in range(5)],
                    "top5_tripletas": [f"{sueltos_ord[0]['num']}-{sueltos_ord[1]['num']}-{sueltos_ord[2]['num']}"],
                    "top20": sueltos_ord[:20]
                },
                "sueltos": sueltos_ord
            }
        else:
            resultado_final[clave] = {"nombre": nombre, "activa": activa, "tipo_juego": "kino"}
            
    return resultado_final
