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
        ("kino_leidsa", "Kino Leidsa TV", 20, 55, "kino"),
        ("primitiva_esp", "La Primitiva (España)", 21, 30, "primitiva"),
        ("euromillones", "Euromillones (Europa)", 21, 30, "euromillones")
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
            
            top5_pales_con_fuerza = []
            for i in range(5):
                p_str = f"{sueltos_ord[i]['num']} - {sueltos_ord[i+1]['num']}"
                fuerza_pale = round((sueltos_ord[i]['fuerza'] + sueltos_ord[i+1]['fuerza']) / 2, 1)
                top5_pales_con_fuerza.append({"pale": p_str, "fuerza": fuerza_pale})

            resultado_final[clave] = {
                "nombre": nombre, "activa": activa, "tipo_juego": "quiniela",
                "tiro_fijo": {"num": sueltos_ord[0]['num'], "virado": sueltos_ord[0]['num'][::-1], "fuerza": 99.6, "palé_titan": f"{sueltos_ord[0]['num']}-{sueltos_ord[1]['num']}"},
                "rankings": {
                    "top5_nums": sueltos_ord[:5],
                    "top5_pales": top5_pales_con_fuerza,
                    "top5_tripletas": [f"{sueltos_ord[0]['num']}-{sueltos_ord[1]['num']}-{sueltos_ord[2]['num']}"],
                    "top20": sueltos_ord[:20]
                },
                "sueltos": sueltos_ord
            }
        elif tipo == "kino":
            kino_duenos = ["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), 10))]
            resultado_final[clave] = {
                "nombre": nombre, "activa": activa, "tipo_juego": "kino",
                "kino_data": {"duenos": kino_duenos}
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
