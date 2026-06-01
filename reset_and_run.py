#!/usr/bin/env python3
"""Inicializador opcional para ambientes que precisam de pequeno atraso."""

import logging
import time


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("Aguardando 5 segundos antes de iniciar o bot.")
    time.sleep(5)

    import bot

    bot.main()
