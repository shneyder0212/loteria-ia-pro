SHNEYDER IA PRO — MEMORIA VIVA VERIFICADA (VERSIÓN FINAL)

CAMBIOS PRINCIPALES
1. Sincroniza resultados automáticamente después de los principales horarios RD.
2. Antes de cada corte (05:00, 13:15, 19:00 RD) vuelve a intentar actualizar memoria.
3. Un resultado RD solo entra si dos fuentes coinciden.
4. Comprueba la fecha mostrada por la fuente para evitar guardar el sorteo de ayer como si fuera hoy.
5. Añadidos adaptadores Anguila 10AM, 1PM, 6PM y 9PM.
6. Añadido Super Kino TV con 20 resultados y motor propio de 10 números.
7. Predicciones congeladas: no cambian después de publicarse.
8. Evaluación automática 0/1/2/3 aciertos cuando llega el resultado.
9. Ranking de la lotería RD donde el motor ha rendido mejor por backtesting.
10. Alerta Roja/Jugada Maestra solo cuando supera filtros estadísticos.
11. España mantiene SELAE como fuente oficial y motores separados de quiniela RD.
12. SQLite usa DB_PATH y está preparada para Persistent Disk de Render.

RENDER
El render.yaml usa:
DB_PATH=/var/data/loteria_master_ai.db
Persistent Disk: /var/data
Start: uvicorn servidor_movil:app --host 0.0.0.0 --port $PORT

Si ya tienes una base con memoria importante, NO la borres: copia esa DB al disco persistente.
Si empiezas desde cero, la app irá acumulando resultados verificados.

ENDPOINTS
/ping
/api/estado
/api/sincronizar
/api/verificar/{clave}
/api/memoria/{clave}
/api/corte/manana
/api/corte/tarde
/api/corte/noche
/api/estudios-hoy
/api/evaluar-hoy
/api/mejor-loteria
/api/alerta-roja/{clave}

IMPORTANTE
El software está diseñado para fallar de forma segura: si las fuentes no coinciden o cambia el HTML, marca PENDIENTE y NO inventa números de resultados.
No puede garantizar ganar una lotería ni 2/3, 3/3, 80% o 100% de aciertos futuros.


Ver README_TOTAL_VIGILANCIA.txt para los motores ampliados.
