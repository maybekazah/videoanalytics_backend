from api.configs.logger import setup_logging
import logging
setup_logging()


class Singletone(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            logging.info(f"Создание нового инстанса {cls.__name__}")
            cls._instances[cls] = super(Singletone, cls).__call__(*args, **kwargs)
        else:
            logging.debug(f"Используется существующий инстанс {cls.__name__}")
        
        logging.debug(f"Адрес объекта {cls.__name__}: {id(cls._instances[cls])}")
        return cls._instances[cls]
