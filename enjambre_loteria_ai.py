import random
from datetime import datetime, timedelta

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

def obtener_tiempos():
    ahora_utc = datetime.utcnow()
    hora_rd = ahora_utc - timedelta(hours=4)
    hora_esp = ahora_utc + timedelta(hours=2)
    return hora_rd, hora_esp, hora_rd.strftime("%d/%m/%Y"), DIAS_SEMANA[hora_rd.weekday()]

def calcular_enjambre_ia():
    hora_rd, hora_esp, _, dia_nombre = obtener_tiempos()
    seed_base = int(hora_rd.strftime("%Y%m%d"))
    es_lunes_domingo = dia_nombre in ["Lunes", "Domingo"]
    
    rng = random.Random(seed_base + (77 if es_lunes_domingo else 33) + hora_rd.hour)

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
        ("kino_leidsa", "Kino Leidsa TV", 20, 55, "kino", "rd", "Nacional Noche (8:50 PM)"),
        ("primitiva_esp", "La Primitiva (España)", 21, 30, "primitiva", "esp", "Euromillones (Europa)"),
        ("euromillones", "Euromillones (Europa)", 21, 30, "euromillones", "esp", "La Primitiva (España)")
    ]

    minutos_actuales_rd = hora_rd.hour * 60 + hora_rd.minute
    minutos_actuales_esp = hora_esp.hour * 60 + hora_esp.minute
    
    resultado_final = {}

    for clave, nombre, h_cierre, m_cierre, tipo, region, respaldo in salas_config:
        cierre_minutos = h_cierre * 60 + m_cierre
        minutos_actuales = minutos_actuales_esp if region == "esp" else minutos_actuales_rd
        
        # Dejamos que 'activa' sea True o False según la hora, pero NUNCA filtramos la sala para que siempre aparezca en las pestañas
        activa = (minutos_actuales <= cierre_minutos)

        if tipo == "quiniela":
            decenas_disponibles = [
                ("[00-09]", "Decena [00-09]"), ("[10-19]", "Decena [10-19]"),
                ("[20-29]", "Decena [20-29]"), ("[30-39]", "Decena [30-39]"),
                ("[40-49]", "Decena [40-49]"), ("[50-59]", "Decena [50-59]"),
                ("[60-69]", "Decena [60-69]"), ("[70-79]", "Decena [70-79]"),
                ("[80-89]", "Decena [80-89]"), ("[90-99]", "Decena [90-99]")
            ]
            decenas_elegidas = rng.sample(decenas_disponibles, 3)
            
            pool_numeros = [f"{n:02d}" for n in range(100)]
            rng.shuffle(pool_numeros)
            
            sueltos = []
            for i in range(25):
                fuerza_val = round(99.9 - (i * 0.4), 1)
                sueltos.append({"num": pool_numeros[i], "fuerza": fuerza_val})
            
            sueltos_ord = sorted(sueltos, key=lambda x: x['fuerza'], reverse=True)
            
            n1, n2, n3 = sueltos_ord[0]['num'], sueltos_ord[1]['num'], sueltos_ord[2]['num']
            
            top5_pales_con_fuerza = []
            for i in range(5):
                p_str = f"{sueltos_ord[i]['num']} - {sueltos_ord[i+1]['num']}"
                fuerza_pale = round((sueltos_ord[i]['fuerza'] + sueltos_ord[i+1]['fuerza']) / 2, 1)
                top5_pales_con_fuerza.append({"pale": p_str, "fuerza": fuerza_pale})

            tripleta_str = f"{n1} - {n2} - {n3}"
            
            num_base_int = int(n1)
            plus_one = f"{ (num_base_int + 1) % 100:02d }"
            minus_one = f"{ (num_base_int - 1) % 100:02d }"

            dictamen = {
                "flujo": "ANCLAJE TRIPLE 3-DECENAS",
                "decenas_clave": f"{decenas_elegidas[0][1]}, {decenas_elegidas[1][1]}, {decenas_elegidas[2][1]}",
                "terminales": f"Term. {rng.randint(1,9)}, {rng.randint(0,9)}",
                "pareja": rng.choice(["MÁXIMA", "MEDIA", "ALTA"]),
                "digito_fuerte": f"Dígitos {rng.randint(1,5)}, {rng.randint(6,9)}",
                "inercia": f"{dia_nombre}: Vigente",
                "foco_principal": decenas_elegidas[0][1],
                "sala_objetivo": nombre,
                "respaldo": respaldo,
                "tres_numeros": [n1, n2, n3],
                "dos_pales": [f"[{n1} - {n2}]", f"[{n2} - {n3}]"],
                "tripleta": tripleta_str,
                "cobertura": f"Lateral +1 / -1: [[+1: {plus_one}] / [-1: {minus_one}]]",
                "pale_reves": f"Palé Revés: [{n2[1]}{n2[0]} - {n1}]"
            }

            resultado_final[clave] = {
                "nombre": nombre, "activa": activa, "tipo_juego": "quiniela",
                "dictamen": dictamen,
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
