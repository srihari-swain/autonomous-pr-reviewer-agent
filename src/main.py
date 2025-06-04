from src.utils.config_loader import read_base_config
import uvicorn

CONFIG = read_base_config()

if __name__ == "__main__":
    uvicorn.run(
        CONFIG["API"]["app"],
        host=CONFIG["API"]["host"],
        port=CONFIG["API"]["port"],
        reload=CONFIG.get("reload", False),
        workers=CONFIG.get("workers", 1)
    )