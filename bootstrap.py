import json
from pathlib import Path
from memoria import guardar_observado, contar_trabajo, guardar_estado

BOOTSTRAP_FILE = Path(__file__).with_name("bootstrap_historico.json")

def importar_bootstrap():
    if not BOOTSTRAP_FILE.exists():
        return {"estado":"SIN_ARCHIVO","importados":0}
    data=json.loads(BOOTSTRAP_FILE.read_text(encoding="utf-8"))
    imported=0
    for r in data.get("records",[]):
        ok=guardar_observado(
            r["pais"],r["clave"],r["nombre"],r["tipo"],r["fecha"],
            {"numeros":r["numeros"]},
            r.get("fuente","bootstrap"),
            r["fecha"]
        )
        if ok:
            imported+=1
    estado={
        "estado":"OK",
        "registros_procesados":imported,
        "memoria_utilizable":contar_trabajo(),
        "nota":data.get("source_note","")
    }
    guardar_estado("bootstrap",estado)
    return estado
