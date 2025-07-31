import os
from dotenv import load_dotenv
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    load_dotenv()
    return {
        "DB_PATH": os.getenv("DB_PATH", "library.db"),
        "HOST": os.getenv("HOST", "0.0.0.0"),
        "PORT": os.getenv("PORT", "8080"),
    }

