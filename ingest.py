from __future__ import annotations

from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from IngestionPipeline.populate_qdrant import populate_qdrant


def run_ingestion_job() -> None:
	started_at = datetime.now().isoformat()
	print(f"[APScheduler] Starting ingestion at {started_at}")
	try:
		populate_qdrant()
		print("[APScheduler] Ingestion completed")
	except Exception as exc:
		print(f"[APScheduler] Ingestion failed: {exc}")


def main() -> None:
	scheduler = BlockingScheduler()
	scheduler.add_job(
		run_ingestion_job,
		trigger="interval",
		hours=24,
		next_run_time=datetime.now(),
		id="daily_qdrant_ingestion",
		replace_existing=True,
	)

	print("[APScheduler] Scheduler started. Running now, then every 24 hours.")
	scheduler.start()


if __name__ == "__main__":
	main()
