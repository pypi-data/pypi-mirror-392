"""
TeleBot Wizard - Custom Exceptions
Bu modul wizard kutubxonasi uchun maxsus xatolik sinflarini o'z ichiga oladi.
Author: Yoqubov Javohir
Version: 1.0.0
"""

__all__ = ["WizardError", "ConfigurationError", "GenerationError", "ValidationError"]


class WizardError(Exception):
    
    def __init__(self, message: str, error_code: str = None):
        
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "WIZARD_ERROR"
        
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ConfigurationError(WizardError):
    
    def __init__(self, message: str):
        super().__init__(message, "CONFIG_ERROR")


class GenerationError(WizardError):
    
    def __init__(self, message: str):
        super().__init__(message, "GENERATION_ERROR")


class ValidationError(WizardError):
    
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")