# ============================================
# dsf_enginexai_sdk/__init__.py
# ============================================
"""SDK de Python para la API de DSF EngineXAI - Explainable AI Scoring"""

__version__ = '1.0.2'  
__author__ = 'Jaime Alexander Jimenez'
__email__ = 'contacto@dsfuptech.cloud'

from .client import CreditScoreClient
from .exceptions import ValidationError, LicenseError, APIError

__all__ = [
    'CreditScoreClient',
    'ValidationError',
    'LicenseError',
    'APIError'
]