from apscheduler.schedulers.blocking import BlockingScheduler
from automate_algo_trading import pairs_trading_algo

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=9, minute=57)
def timed_job():
	print("Start Pairs Trading Algo...")
	pairs_trading_algo()
	print("End Pairs Trading Algo...")

sched.start()