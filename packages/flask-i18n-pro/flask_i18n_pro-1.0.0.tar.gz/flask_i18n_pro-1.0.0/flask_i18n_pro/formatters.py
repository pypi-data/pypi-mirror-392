"""
Locale-aware formatting functions for dates, numbers, and currencies.

Supports:
- English
- Russian (Cyrillic)
- Mongolian (Cyrillic)
- Chinese
- And any locale supported by Babel
"""

from flask_babel import (
    format_date,
    format_datetime,
    format_time,
    format_number,
    format_currency,
    format_percent,
    ngettext,
    pgettext,
)


# ============================================================================
# Date and Time Formatting
# ============================================================================

def format_delivery_date(date):
    """
    Format a delivery date in the user's locale.

    Examples:
        en: "Dec 25, 2023"
        ru: "25 дек. 2023 г."
        mn: "2023 оны 12-р сарын 25"
        zh: "2023年12月25日"

    Args:
        date: datetime.date or datetime.datetime object

    Returns:
        Formatted date string in user's locale
    """
    if not date:
        return ""
    return format_date(date, format='medium')


def format_order_datetime(dt):
    """
    Format an order datetime in the user's locale.

    Examples:
        en: "Dec 25, 2023, 2:30 PM"
        ru: "25 дек. 2023 г., 14:30"
        mn: "2023 оны 12-р сарын 25, 14:30"
        zh: "2023年12月25日 下午2:30"

    Args:
        dt: datetime.datetime object

    Returns:
        Formatted datetime string in user's locale
    """
    if not dt:
        return ""
    return format_datetime(dt, format='medium')


def format_short_date(date):
    """
    Format a date in short format (numbers only).

    Examples:
        en: "12/25/23"
        ru: "25.12.2023"
        mn: "2023.12.25"
        zh: "2023/12/25"

    Args:
        date: datetime.date or datetime.datetime object

    Returns:
        Formatted date string in user's locale
    """
    if not date:
        return ""
    return format_date(date, format='short')


def format_time_only(dt):
    """
    Format time only (no date).

    Examples:
        en: "2:30 PM"
        ru: "14:30"
        mn: "14:30"
        zh: "下午2:30"

    Args:
        dt: datetime.datetime object

    Returns:
        Formatted time string in user's locale
    """
    if not dt:
        return ""
    return format_time(dt, format='short')


# ============================================================================
# Number Formatting
# ============================================================================

def format_price(amount, currency='USD'):
    """
    Format a price with currency symbol in the user's locale.

    Cyrillic-aware formatting:
    - Russian uses space as thousand separator, comma for decimals
    - Mongolian uses comma for thousands, period for decimals
    - Chinese uses comma for thousands

    Examples:
        en: "$15,000.00"
        ru (RUB): "15 000,00 ₽"
        mn (MNT): "15,000.00 ₮"
        zh (CNY): "¥15,000.00"

    Args:
        amount: Numeric amount
        currency: Currency code (ISO 4217: USD, EUR, RUB, MNT, CNY, etc.)

    Returns:
        Formatted currency string in user's locale

    Supported Currencies:
        - USD: US Dollar ($)
        - EUR: Euro (€)
        - RUB: Russian Ruble (₽)
        - MNT: Mongolian Tugrik (₮)
        - CNY: Chinese Yuan (¥)
        - And 100+ more via Babel
    """
    if amount is None:
        return ""
    return format_currency(amount, currency)


def format_weight(weight):
    """
    Format a weight value in the user's locale.

    Examples:
        en: "1,250.5"
        ru: "1 250,5" (Cyrillic: space separator, comma decimal)
        mn: "1,250.5"
        zh: "1,250.5"

    Args:
        weight: Numeric weight value

    Returns:
        Formatted number string in user's locale
    """
    if weight is None:
        return ""
    return format_number(weight)


def format_percentage(value):
    """
    Format a percentage in the user's locale.

    Examples:
        en: "85%"
        ru: "85 %" (Cyrillic: space before %)
        mn: "85%"
        zh: "85%"

    Args:
        value: Decimal value (0.85 for 85%, or 85 for 85%)

    Returns:
        Formatted percentage string in user's locale

    Note:
        Pass decimal values (0.85) not percentages (85)
    """
    if value is None:
        return ""
    return format_percent(value)


# ============================================================================
# Pluralization
# ============================================================================
# These functions handle complex pluralization rules for different languages.
#
# English: 1 vs. 2+ (simple)
# Russian: 1, 2-4, 5+ (complex)
# Mongolian: 1, 2+ (simple)
# Chinese: No pluralization (same form)

def format_product_count(count):
    """
    Format product count with proper pluralization.

    Examples:
        en: "1 product", "5 products"
        ru: "1 продукт", "2 продукта", "5 продуктов"
        mn: "1 бүтээгдэхүүн", "5 бүтээгдэхүүн"
        zh: "1 个产品", "5 个产品"

    Args:
        count: Number of products (int)

    Returns:
        Formatted string with count and properly pluralized form

    Pluralization Rules:
        - English: 1 → product, else → products
        - Russian: 1 → продукт, 2-4 → продукта, 5+ → продуктов
        - Mongolian: same form always
        - Chinese: same form always
    """
    return ngettext(
        "%(count)d product",
        "%(count)d products",
        count
    ) % {'count': count}


def format_delivery_count(count):
    """
    Format delivery count with proper pluralization.

    Args:
        count: Number of deliveries

    Returns:
        Formatted string (e.g., "3 deliveries")
    """
    return ngettext(
        "%(count)d delivery",
        "%(count)d deliveries",
        count
    ) % {'count': count}


def format_return_count(count):
    """
    Format return count with proper pluralization.

    Args:
        count: Number of returns

    Returns:
        Formatted string (e.g., "2 returns")
    """
    return ngettext(
        "%(count)d return",
        "%(count)d returns",
        count
    ) % {'count': count}


def format_item_count(count):
    """
    Format generic item count with proper pluralization.

    Args:
        count: Number of items

    Returns:
        Formatted string (e.g., "10 items")
    """
    return ngettext(
        "%(count)d item",
        "%(count)d items",
        count
    ) % {'count': count}


# ============================================================================
# Context-Aware Translations
# ============================================================================

def translate_with_context(message, context='general'):
    """
    Translate a message with context to disambiguate meanings.

    This solves the problem of homonyms - words that look the same
    but have different meanings in different contexts.

    Examples:
        "open" can mean:
        - translate_with_context("open", "store_status") → "открыт" (is open)
        - translate_with_context("open", "order_status") → "открыт" (not fulfilled)
        - translate_with_context("open", "action") → "открыть" (to open)

    Args:
        message: String to translate
        context: Context identifier (string)

    Returns:
        Translated string for the given context

    Usage in Translation Files (.po):
        msgctxt "store_status"
        msgid "open"
        msgstr "открыт"

        msgctxt "action"
        msgid "open"
        msgstr "открыть"

    Note:
        This uses gettext's context feature (pgettext).
        Without context, translations can be ambiguous.
    """
    return pgettext(context, message)


# ============================================================================
# Template Filter Registration
# ============================================================================

def register_filters(app):
    """
    Register all formatting functions as Jinja2 template filters.

    Usage in Templates:
        Date/Time:
        {{ order.created_at|format_order_datetime }}
        {{ delivery.date|format_delivery_date }}
        {{ product.updated_at|format_short_date }}

        Numbers/Currency:
        {{ product.price|format_price('USD') }}
        {{ product.weight|format_weight }}
        {{ discount|format_percentage }}

        Counts:
        {{ products|length|format_product_count }}
        {{ deliveries|length|format_delivery_count }}

    Args:
        app: Flask application instance
    """
    # Date/time filters
    app.jinja_env.filters['format_delivery_date'] = format_delivery_date
    app.jinja_env.filters['format_order_datetime'] = format_order_datetime
    app.jinja_env.filters['format_short_date'] = format_short_date
    app.jinja_env.filters['format_time_only'] = format_time_only

    # Number filters
    app.jinja_env.filters['format_price'] = format_price
    app.jinja_env.filters['format_weight'] = format_weight
    app.jinja_env.filters['format_percentage'] = format_percentage

    # Pluralization filters
    app.jinja_env.filters['format_product_count'] = format_product_count
    app.jinja_env.filters['format_delivery_count'] = format_delivery_count
    app.jinja_env.filters['format_return_count'] = format_return_count
    app.jinja_env.filters['format_item_count'] = format_item_count
