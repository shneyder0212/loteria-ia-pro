# [CALCULADOR DE RANKINGS - TOP 5 Y TOP 20]
        # Ordenamos los sueltos por fuerza
        sueltos_ordenados = sorted(sueltos_sala, key=lambda x: x['fuerza'], reverse=True)
        top5_nums = sueltos_ordenados[:5]
        
        # Generamos pales basados en los mejores 5
        top5_pales = []
        for i in range(4):
            top5_pales.append(f"{sueltos_ordenados[i]['num']} - {sueltos_ordenados[i+1]['num']}")
            
        # Generamos tripletas basadas en los mejores 3
        tripleta_top = f"{sueltos_ordenados[0]['num']} - {sueltos_ordenados[1]['num']} - {sueltos_ordenados[2]['num']}"

        # Agregamos los rankings al objeto de la sala
        resultado_final[clave]["rankings"] = {
            "top5_nums": top5_nums,
            "top5_pales": top5_pales,
            "top5_tripletas": [tripleta_top, f"{sueltos_ordenados[0]['num']}-{sueltos_ordenados[2]['num']}-{sueltos_ordenados[3]['num']}", "...", "...", "..."],
            "top20": sueltos_ordenados[:20]
        }
