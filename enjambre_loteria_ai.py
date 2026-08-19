def aplicar_regla_virado(self, top_sueltos, umbral=85.0):
        jugadas = []
        vistos = set()

        for item in top_sueltos:
            num = item["numero"]
            fuerza = item["fuerza_ia"]
            lot = item["loteria"]

            if num not in vistos:
                jugadas.append(item)
                vistos.add(num)

            # Blindaje automático si supera el 85%
            if fuerza >= umbral:
                reves = num[::-1] if len(num) == 2 else num
                # Excluir números gemelos (11, 22, 33...) que no tienen virado
                if reves != num and reves not in vistos:
                    fuerza_reves = round(fuerza * 0.90, 1)  # Cobertura fuerte al 90%
                    jugadas.append({
                        "numero": reves,
                        "fuerza_ia": fuerza_reves,
                        "loteria": f"{lot} (VIRADO PROTECCIÓN DE {num})"
                    })
                    vistos.add(reves)

        return sorted(jugadas, key=lambda x: x["fuerza_ia"], reverse=True)
