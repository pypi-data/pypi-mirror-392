import time
from colorama import Fore, init as colorama_init

colorama_init(autoreset=True)

class Logger:
    def __init__(self, logfile="app.log"):
        self.logfile = logfile

    def _timestamp(self):
        return time.strftime("%Y-%m-%d %H:%M:%S")

    def _write_file(self, level, msg):
        """Write plain text (no ANSI colors) to the log file."""
        with open(self.logfile, "a", encoding="utf-8") as f:
            f.write(f"[{self._timestamp()}] [{level}] {msg}\n")

    def _console(self, color, level, msg):
        """Print colorized output to the terminal."""
        print(
            f"{Fore.LIGHTBLACK_EX}{self._timestamp()} "
            f"{color}[{level}]{Fore.WHITE}: {msg}"
        )

    def init(self):
        msg = "Initialized logger"
        self._console(Fore.GREEN, "SUCCES", msg)
        self._write_file("SUCCES", msg)

    def info(self, msg):
        msg = str(msg)
        self._console(Fore.BLUE, "INFO", msg)
        self._write_file("INFO", msg)

    def success(self, msg):
        msg = str(msg)
        self._console(Fore.GREEN, "SUCCESS", msg)
        self._write_file("SUCCESS", msg)

    def warn(self, msg):
        msg = str(msg)
        self._console(Fore.YELLOW, "WARNING", msg)
        self._write_file("WARNING", msg)

    def error(self, msg):
        msg = str(msg)
        self._console(Fore.RED, "ERROR", msg)
        self._write_file("ERROR", msg)

    def critical(self, msg):
        msg = str(msg)
        self._console(Fore.RED + Fore.LIGHTWHITE_EX, "CRITICAL", msg)
        self._write_file("CRITICAL", msg)
