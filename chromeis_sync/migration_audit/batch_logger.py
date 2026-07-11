from datetime import datetime
from pathlib import Path


class BatchLogger:

    def __init__(self, log_dir="logs"):

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.log_file = self.log_dir / f"migration_{timestamp}.log"

    def _write(self, message):

        line = f"[{datetime.now().strftime('%H:%M:%S')}] {message}"

        print(line)

        with open(self.log_file, "a") as f:
            f.write(line + "\n")

    def info(self, message):
        self._write(f"INFO : {message}")

    def success(self, message):
        self._write(f"PASS : {message}")

    def warning(self, message):
        self._write(f"WARN : {message}")

    def error(self, message):
        self._write(f"FAIL : {message}")

    def separator(self):
        self._write("-" * 70)

    def summary(self, result):

        self.separator()

        self.info("Migration Summary")

        self.info(f"Processed : {result.stats.processed}")
        self.info(f"Passed    : {result.stats.passed}")
        self.info(f"Failed    : {result.stats.failed}")
        self.info(f"Skipped   : {result.stats.skipped}")

        self.info(f"Success % : {result.stats.success_rate}")

        self.info(f"Duration  : {result.duration:.2f} sec")

        self.separator()
