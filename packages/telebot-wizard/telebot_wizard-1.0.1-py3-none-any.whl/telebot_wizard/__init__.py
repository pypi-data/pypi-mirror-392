"""
TeleBot Wizard - Zero-Code Bot Builder

Bu kutubxona orqali foydalanuvchilar hech qanday kod yozmasdan
pyTelegramBotAPI yordamida professional Telegram botlar yarata olishadi.

Author: Yoqubov javohir
Version: 1.0.0
Python: 3.8+
License: MIT
"""

from .wizard import BotWizard
from .exceptions import WizardError, ConfigurationError, GenerationError

__version__ = "1.0.0"
__author__ = "Yoqubov Javohir"
__email__ = "rakuzenuz@gmail.com"
__license__ = "MIT"

__all__ = [
    "BotWizard",
    "WizardError", 
    "ConfigurationError",
    "GenerationError"
]