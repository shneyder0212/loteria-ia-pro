import random
from datetime import datetime, timedelta

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

TABLA_JALADERA = {
    "00": ["55", "05", "50"], "01": ["56", "10", "61"], "02": ["57", "20", "72"], "03": ["58", "30", "83"],
    "04": ["59", "40", "94"], "05": ["00", "50", "20"], "06": ["51", "60", "29"], "07": ["52", "70", "25"],
    "08": ["53", "80", "35"], "09": ["54", "90", "45"], "10": ["65", "01", "15"], "11": ["66", "16", "22"],
    "12": ["67", "21", "27"], "13": ["68", "31", "38"], "14": ["69", "41", "49"], "15": ["60", "51", "06"],
    "16": ["61", "11", "66"], "17": ["62", "12", "71"], "18": ["63", "13", "81"], "19": ["64", "14", "91"],
    "20": ["75", "02", "25"], "21": ["76", "12", "26"], "22": ["77", "27", "44"], "23": ["78", "32", "82"],
    "24": ["79", "42", "92"], "25": ["50", "00", "75"], "26": ["62", "71", "18"], "27": ["82", "22", "72"],
    "28": ["82", "46", "73"], "29": ["74", "92", "06"], "30": ["85", "03", "35"], "31": ["86", "13", "36"],
    "32": ["87", "23", "37"], "33": ["88", "38", "99"], "34": ["89", "43", "39"], "35": ["80", "53", "05"],
    "36": ["81", "63", "31"], "37": ["82", "73", "27"], "38": ["83", "33", "93"], "39": ["84", "93", "43"],
    "40": ["95", "04", "45"], "41": ["96", "14", "46"], "42": ["97", "24", "47"], "43": ["98", "34", "48"],
    "44": ["99", "49", "11"], "45": ["90", "54", "05"], "46": ["91", "64", "14"], "47": ["92", "74", "13"],
    "48": ["93", "84", "24"], "49": ["94", "99", "14"], "50": ["05", "00", "55"], "51": ["06", "15", "60"],
    "52": ["07", "25", "70"], "53": ["08", "35", "80"], "54": ["09", "45", "90"], "55": ["00", "50", "77"],
    "56": ["01", "16", "61"], "57": ["02", "26", "71"], "58": ["03", "36", "81"], "59": ["04", "46", "91"],
    "60": ["15", "06", "51"], "61": ["16", "66", "11"], "62": ["17", "26", "76"], "63": ["18", "36", "86"],
    "64": ["19", "46", "96"], "65": ["10", "56", "01"], "66": ["11", "61", "33"], "67": ["12", "71", "21"],
    "68": ["13", "81", "31"], "69": ["14", "91", "41"], "70": ["25", "07", "52"], "71": ["26", "17", "62"],
    "72": ["27", "22", "77"], "73": ["28", "37", "82"], "74": ["29", "47", "92"], "75": ["20", "57", "02"],
    "76": ["21", "67", "12"], "77": ["22", "72", "55"], "78": ["23", "87", "32"], "79": ["24", "97", "42"],
    "80": ["35", "08", "53"], "81": ["36", "18", "63"], "82": ["37", "28", "73"], "83": ["38", "33", "88"],
    "84": ["39", "48", "93"], "85": ["30", "58", "03"], "86": ["31", "68", "13"], "87": ["32", "78", "23"],
    "88": ["33", "83", "00"], "89": ["34", "98", "44"], "90": ["45", "09", "54"], "91": ["46", "19", "64"],
    "92": ["47", "29", "74"], "93": ["48", "39", "84"], "94": ["49", "99", "44"], "95": ["40", "59", "04"],
    "96": ["41", "69", "14"], "97": ["42", "79", "24"], "98": ["43", "89", "34"], "99": ["44", "94", "66"]
}

def obtener_jalamatico(num_str):
    return TABLA_JALADERA.get(num_str, [num_str[::-1], "{:02d}".format((int(num_str)+10)%100), "{:02d}".format((int(num_str)+50)%100)])

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
        ("lotedom", "LoteDom", 12, 0, "quiniela"),
        ("kino_leidsa", "Kino Leidsa TV", 20, 55, "kino"),
        ("primitiva_esp", "La Primitiva (España)", 21, 30, "primitiva"),
        ("euromillones", "Euromillones (Europa)", 21, 30, "euromillones")
    ]

    hora_actual_minutos = hora_rd.hour * 60 + hora_rd.minute
    resultado_final = {}
    usados = []

    for clave, nombre, h_cierre, m_cierre, tipo in salas_config:
        cierre_minutos = h_cierre * 60 + m_cierre
        activa = hora_actual_minutos <= cierre_minutos

        if tipo == "quiniela":
            decena_base = rng.choice([10, 30, 40, 70, 80])
            terminales = rng.sample([2, 3, 5, 7, 8], 3)
            n1 = "{:02d}".format(decena_base + terminales[0])
            n2 = "{:02d}".format(decena_base + terminales[1])
            jals = obtener_jalamatico(n1)
            n3 = jals[1]
            
            while n1 in usados:
                n1 = "{:02d}".format((int(n1) + 3) % 100)
            usados.append(n1)

            resultado_final[clave] = {
                "nombre": nombre, "activa": activa, "tipo_juego": "quiniela",
                "tiro_fijo": {"num": n1, "virado": n1[::-1], "fuerza": 99.6, "palé_titan": f"{n1} - {n2}", "lot_fuerte": nombre},
                "jugada_maestra": {"numeros_3": [n1, n2, n3], "pale_1": f"{n1}-{n2}", "pale_2": f"{n1}-{n3}", "tripleta": f"{n1}-{n2}-{n3}"},
                "sueltos": [{"num": n1, "fuerza": 99.6, "tipo": "Principal", "lot": nombre}, {"num": n2, "fuerza": 98.2, "tipo": "Terminal", "lot": nombre}, {"num": n3, "fuerza": 97.4, "tipo": "Jaladera", "lot": nombre}]
            }
        elif tipo == "kino":
            kino_duenos = ["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), 10))]
            def gen_kino(cant): return " - ".join(["{:02d}".format(n) for n in sorted(rng.sample(range(1, 81), cant))])
            resultado_final[clave] = {
                "nombre": nombre, "activa": activa, "tipo_juego": "kino",
                "tiro_fijo": {"num": kino_duenos[0], "virado": "--", "fuerza": 98.6, "palé_titan": "Bloque 5 Activo", "lot_fuerte": nombre},
                "kino_data": {
                    "duenos": kino_duenos,
                    "bloques_5": [{"bloque": gen_kino(5), "paridad": "3 Imp / 2 Par", "fuerza": 98.6}],
                    "bloques_7": [{"bloque": gen_kino(7), "paridad": "4 Imp / 3 Par", "fuerza": 99.1}]
                }
            }
        elif tipo == "primitiva":
            prim_base = ["{:02d}".format(n) for n in sorted(rng.sample(range(1, 50), 8))]
            resultado_final[clave] = {
                "nombre": nombre, "activa": activa, "tipo_juego": "primitiva",
                "tiro_fijo": {"num": prim_base[0], "virado": "--", "fuerza": 98.9, "palé_titan": f"Reintegro: {rng.randint(0,9)}", "lot_fuerte": nombre},
                "primitiva_data": {"reintegro": str(rng.randint(0,9)), "complementario": "{:02d}".format(rng.randint(1,49)), "numeros_base": prim_base}
            }
        elif tipo == "euromillones":
            euro_nums = sorted(rng.sample(range(1, 51), 5))
            e1, e2 = "{:02d}".format(rng.randint(1, 12)), "{:02d}".format(rng.randint(1, 12))
            resultado_final[clave] = {
                "nombre": nombre, "activa": activa, "tipo_juego": "euromillones",
                "tiro_fijo": {"num": euro_nums[0], "virado": "--", "fuerza": 99.4, "palé_titan": f"Estrellas: {e1} - {e2}", "lot_fuerte": nombre},
                "euro_data": {"estrellas_fijas": [e1, e2], "red_afinidad": [str(n) for n in euro_nums]}
            }
    return resultado_final
