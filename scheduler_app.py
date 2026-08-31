from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo
from estudios_diarios import ejecutar_corte

TZ="America/Santo_Domingo"
scheduler=BackgroundScheduler(timezone=ZoneInfo(TZ))

def iniciar_scheduler():
    if scheduler.running:
        return
    scheduler.add_job(lambda: ejecutar_corte("manana"), CronTrigger(hour=5, minute=0, timezone=TZ), id="corte_manana", replace_existing=True)
    scheduler.add_job(lambda: ejecutar_corte("tarde"), CronTrigger(hour=13, minute=15, timezone=TZ), id="corte_tarde", replace_existing=True)
    scheduler.add_job(lambda: ejecutar_corte("noche"), CronTrigger(hour=19, minute=0, timezone=TZ), id="corte_noche", replace_existing=True)
    scheduler.start()
