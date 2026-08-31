SHNEYDER IA PRO - CORTES DIARIOS + MEMORIA VIVA

NUEVO PLAN DE ESTUDIO (HORA RD)
05:00 - ESTUDIO MAÑANA
  Anguila 10 AM
  Primera Día
  LoteDom
  Lotería Real
  Anguila 1 PM

13:15 - REESTUDIO TARDE
  Gana Más
  Anguila 6 PM
  Loteka

19:00 - REESTUDIO NOCTURNO
  Primera Noche
  Nacional Noche
  Leidsa
  Anguila 9 PM
  Kino (queda reservado hasta añadir un modelo específico)

POR QUÉ 3 CORTES
Los resultados conocidos durante el día pueden convertirse en nuevas señales:
revés, atracción temporal, coaparición, terminales y decenas.
El bloque de noche no usa únicamente lo que se sabía a las 5 AM.

CONGELACIÓN
Cada predicción se guarda una sola vez por:
fecha + corte + lotería.
Después no cambia automáticamente. Esto permite evaluar de verdad si acertó.

ENDPOINTS NUEVOS
/api/corte/manana
/api/corte/tarde
/api/corte/noche
/api/estudios-hoy

SCHEDULER
APScheduler ejecuta los tres cortes con timezone America/Santo_Domingo.
Requiere que el servicio web esté encendido.

RENDER
render.yaml mantiene:
- Web Service Starter
- Persistent Disk /var/data
- DB_PATH=/var/data/loteria_master_ai.db
- health check /ping
- Cron Job cada 5 minutos para ping externo

IMPORTANTE
Un ping no mejora las probabilidades de la lotería. Solo ayuda con disponibilidad/monitorización.
Ninguna función de este proyecto garantiza 2/3, 3/3, 80% o 100% de aciertos futuros.
El objetivo es medir y mejorar el rendimiento usando datos verificados y backtesting.


ALERTA ROJA - JUGADA MAESTRA
La alerta roja NO aparece todos los días.
Solo aparece para quinielas RD cuando TODOS estos filtros se cumplen:
- mínimo 80 muestras evaluables;
- Score del número #1 >= 68;
- promedio del Top 3 >= 60;
- backtesting Top 10 con 2+ aciertos >= 8%;
- al menos 4 señales distintas entre los 3 números principales.

Las señales pueden incluir:
- atraso;
- revés;
- atracción temporal;
- coaparición;
- terminal;
- decena.

Endpoint:
/api/alerta-roja/{clave}

IMPORTANTE
La alerta significa "máxima coincidencia de señales del modelo", no "resultado seguro".
No garantiza 2/3, 3/3, 80% ni 100% de aciertos.
