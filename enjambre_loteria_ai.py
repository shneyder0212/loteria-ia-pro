# Rankings con porcentajes para los Palés
            top5_pales_con_fuerza = []
            for i in range(5):
                p_str = f"{sueltos_ord[i]['num']} - {sueltos_ord[i+1]['num']}"
                # Calculamos un promedio de fuerza para el palé
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
