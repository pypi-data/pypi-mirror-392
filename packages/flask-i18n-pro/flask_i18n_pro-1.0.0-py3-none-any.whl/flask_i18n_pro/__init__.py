"""
Flask-I18N-Pro
==============

Production-grade internationalization for Flask with Cyrillic and Asian language support.

Features:
- 4-tier locale selection (URL > Session > Accept-Language > Default)
- Cyrillic-aware number/currency formatting (Russian, Mongolian, etc.)
- Context-aware translations (disambiguate homonyms)
- Pluralization utilities for multiple languages
- Time-ago formatting with proper plurals
- Template filters for easy use in Jinja2
- Zero blocking API calls (browser-header based)

Usage:
    from flask import Flask
    from flask_i18n_pro import setup_i18n, format_price, time_ago

    app = Flask(__name__)
    app.config['LANGUAGES'] = ['en', 'ru', 'mn', 'zh']
    setup_i18n(app)

    # In routes
    price = format_price(15000, 'MNT')  # Auto-formats per locale

    # In templates
    {{ product.price|format_price }}
    {{ order.created_at|time_ago }}

Author: wallmarkets Team
License: MIT
"""

__version__ = "1.0.0"
__author__ = "wallmarkets Team"
__license__ = "MIT"

from .locale_selector import setup_i18n, get_locale, compile_translations
from .formatters import (
    # Date/time formatting
    format_delivery_date,
    format_order_datetime,
    format_short_date,
    format_time_only,
    # Number formatting
    format_price,
    format_weight,
    format_percentage,
    # Pluralization
    format_product_count,
    format_delivery_count,
    format_return_count,
    format_item_count,
    # Context-aware
    translate_with_context,
)
from .time_utils import time_ago, format_timestamp, is_new

__all__ = [
    # Setup
    "setup_i18n",
    "get_locale",
    "compile_translations",
    # Date/time
    "format_delivery_date",
    "format_order_datetime",
    "format_short_date",
    "format_time_only",
    "time_ago",
    "format_timestamp",
    "is_new",
    # Numbers
    "format_price",
    "format_weight",
    "format_percentage",
    # Pluralization
    "format_product_count",
    "format_delivery_count",
    "format_return_count",
    "format_item_count",
    # Context
    "translate_with_context",
]
