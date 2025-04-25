import datetime
import logging
import os

class Logger():
    def __init__(self, log_to_console=True):
        self.NOTSET = logging.NOTSET
        self.DEBUG = logging.DEBUG
        self.INFO = logging.INFO
        self.WARNING = logging.WARNING
        self.ERROR = logging.ERROR
        self.CRITICAL = logging.CRITICAL
        
        self.log_to_console = log_to_console
        
        f1 = "./Logs/logs.txt"
        
        # Create Logs directory if it does not exist
        if not os.path.exists(f1):
            os.makedirs(os.path.dirname(f1), exist_ok=True)
            with open(f1, "w") as f:
                data = 0
                f.write(str(data))
                f.close()
        else:
            with open(f1, "r+") as f:
                data = int(f.read())
                f.seek(0)
                f.write(str(data + 1))
                f.truncate()
                f.close()
        file = "./Logs/log" + str(data) + ".txt"

        logging.basicConfig(filename=file, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s: %(message)s')
        logging.info(f"Log {data}\n")

    def write(self, data, level = logging.INFO):
        match level:
            case logging.NOTSET:
                pass
            case logging.DEBUG:
                logging.debug(data)
            case logging.INFO:
                logging.info(data)
            case logging.WARNING:
                logging.warning(data)
            case logging.ERROR:
                logging.error(data)
            case logging.CRITICAL:
                logging.critical(data)
            case _:
                pass
        
        if self.log_to_console:
            print(f"[{logging.getLevelName(level)}] {data}")

    # def close(self):
        # self.log.close()
