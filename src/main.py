import logging
from logging.handlers import RotatingFileHandler
import sys
import aiohttp.web
from aiohttp_swagger import setup_swagger
from utils.config import load_config
from models.database import init_db
from routes.books import setup_routes as setup_book_routes
from routes.stats import setup_routes as setup_stats_routes

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

async def create_app() -> aiohttp.web.Application:
    app = aiohttp.web.Application()
    
    # Инициализация логгера
    logger = setup_logging()
    app['logger'] = logger
    logger.info("Starting application initialization")
    
    try:
        config = load_config()
        await init_db(app, config)
        
        setup_book_routes(app)
        setup_stats_routes(app)
        
        setup_swagger(
            app=app,
            swagger_url="/api/doc",
            ui_version=3,
            title="Library API",
            description="RESTful API for library catalog management",
        )
        
        logger.info("Application initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise
    
    return app

if __name__ == "__main__":
    aiohttp.web.run_app(create_app(), port=8080)