import logging
import argparse
from config import get_config
from sync import SyncEngine

def main():
    # Charger la configuration
    config = get_config()

    # Configurer le logging
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    # Initialiser le moteur de synchronisation
    sync_engine = SyncEngine(config)

    # Exécuter la synchronisation
    sync_engine.sync()

if __name__ == "__main__":
    main()