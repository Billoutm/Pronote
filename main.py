#!/usr/bin/env python3
"""Point d entree principal pour la synchronisation PRONOTE -> Notion."""

import logging
import argparse
import sys
from typing import Optional

from config import get_config
from sync import SyncEngine

def setup_logging(log_level: str = "INFO") -> None:
    """Configure le systeme de logging."""
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("pronote_notion_sync.log")
        ]
    )

def parse_args() -> argparse.Namespace:
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Synchronise les devoirs de PRONOTE vers Notion"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mode simulation (aucune modification dans Notion)"
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Desactive l'utilisation de l'IA Mistral"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Niveau de logging"
    )
    parser.add_argument(
        "--headless",
        action="store_false",
        help="Desactive le mode headless (affiche la fenetre Chrome)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=".env",
        help="Chemin vers le fichier .env"
    )
    return parser.parse_args()

def main():
    """Fonction principale."""
    args = parse_args()

    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    try:
        config = get_config(args.config)

        if args.dry_run:
            config.DRY_RUN = True
            logger.info("Mode DRY-RUN active")

        if args.no_ai:
            config.AI_ENABLED = False
            logger.info("IA desactivee par argument CLI")

        if not args.headless:
            config.HEADLESS = False
            logger.info("Mode visible (fenetre Chrome affichee)")

        sync_engine = SyncEngine(config)

        try:
            stats = sync_engine.sync()
        finally:
            sync_engine.close()

        if stats.get("errors", 0) > 0:
            logger.warning(f"Synchronisation terminee avec des erreurs: {stats}")
            return 1

        logger.info(f"Synchronisation terminee avec succes: {stats}")
        return 0

    except ValueError as e:
        logger.error(f"Erreur de configuration: {e}")
        logger.error("Veuillez verifier que toutes les variables d environnement sont definies dans .env")
        return 1
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
