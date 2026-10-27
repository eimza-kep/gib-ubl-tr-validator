# -*- coding: utf-8 -*-
"""
GİB UBL-TR 1.2 e-Fatura ve e-Arşiv XML Şema & İş Kuralı Doğrulayıcı
"""

__version__ = "1.0.0"
__author__ = "eimza-kep"

from .validator import UBLTRValidator, ValidationResult, ValidationError
from .generator import generate_mock_invoice

__all__ = ["UBLTRValidator", "ValidationResult", "ValidationError", "generate_mock_invoice"]
