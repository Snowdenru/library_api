import logging
import sys
from logging.handlers import RotatingFileHandler

import aiohttp.web

from utils.config import load_config
from models.database import init_db

def setup_logging():
    logger = logging.getLogger('library_api')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler('library_api.log', maxBytes=5*1024*1024, backupCount=3)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


async def create_app():
    app = aiohttp.web.Application()

    logger = setup_logging()
    app['logger'] = logger

    logger.info("Starting application initialization")

    try:
        config = load_config()
        await init_db(app, config)
  
        logger.info("Application initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        logger.exception(f"Failed to initialize application exception:")
        raise

    return app



if __name__== "__main__":
    aiohttp.web.run_app(create_app(), port=8080)