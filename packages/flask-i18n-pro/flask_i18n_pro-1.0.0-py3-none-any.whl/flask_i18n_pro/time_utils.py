"""
Time and relative timestamp utilities.

Provides "time ago" formatting with proper pluralization for all languages.
"""

from datetime import datetime, timezone
from typing import Union

from flask_babel import lazy_gettext as _l
from flask_babel import ngettext
from flask_babel.speaklater import LazyString


def time_ago(dt: datetime) -> Union[str, LazyString]:
    """
    Convert a datetime to a relative time string (e.g., '2 days ago').

    Properly handles pluralization for all languages:
    - English: "1 minute ago" vs "2 minutes ago"
    - Russian: "1 минуту назад" vs "2 минуты назад" vs "5 минут назад"
    - Mongolian: "1 минутын өмнө" vs "5 минутын өмнө"
    - Chinese: "1 分钟前" vs "5 分钟前"

    Args:
        dt: DateTime object to convert (timezone-aware or naive)

    Returns:
        Localized relative time string

    Examples:
        >>> from datetime import datetime, timedelta, timezone
        >>> now = datetime.now(timezone.utc)
        >>> time_ago(now - timedelta(minutes=5))
        "5 minutes ago"

        >>> time_ago(now - timedelta(hours=2))
        "2 hours ago"

        >>> time_ago(now - timedelta(days=3))
        "3 days ago"

    Time Ranges:
        - < 60s: "Just now"
        - < 1 hour: "X minutes ago"
        - < 1 day: "X hours ago"
        - < 1 week: "X days ago"
        - < 1 month: "X weeks ago"
        - < 1 year: "X months ago"
        - >= 1 year: "X years ago"
    """
    if not dt:
        return _l("Unknown")

    # Ensure timezone-aware datetime
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    diff = now - dt
    seconds = diff.total_seconds()

    if seconds < 60:
        return _l("Just now")

    elif seconds < 3600:  # Less than 1 hour
        minutes = int(seconds / 60)
        return ngettext(
            "%(num)d minute ago",
            "%(num)d minutes ago",
            minutes
        ) % {"num": minutes}

    elif seconds < 86400:  # Less than 1 day
        hours = int(seconds / 3600)
        return ngettext(
            "%(num)d hour ago",
            "%(num)d hours ago",
            hours
        ) % {"num": hours}

    elif seconds < 604800:  # Less than 1 week
        days = int(seconds / 86400)
        return ngettext(
            "%(num)d day ago",
            "%(num)d days ago",
            days
        ) % {"num": days}

    elif seconds < 2592000:  # Less than 30 days
        weeks = int(seconds / 604800)
        return ngettext(
            "%(num)d week ago",
            "%(num)d weeks ago",
            weeks
        ) % {"num": weeks}

    elif seconds < 31536000:  # Less than 1 year
        months = int(seconds / 2592000)
        return ngettext(
            "%(num)d month ago",
            "%(num)d months ago",
            months
        ) % {"num": months}

    else:
        years = int(seconds / 31536000)
        return ngettext(
            "%(num)d year ago",
            "%(num)d years ago",
            years
        ) % {"num": years}


def format_timestamp(dt: datetime, format_string: str = "%Y-%m-%d %H:%M") -> str:
    """
    Format a datetime object with a specific format string.

    Args:
        dt: DateTime object to format
        format_string: Python datetime format string (default: YYYY-MM-DD HH:MM)

    Returns:
        Formatted datetime string

    Examples:
        >>> dt = datetime(2023, 12, 25, 14, 30)
        >>> format_timestamp(dt)
        "2023-12-25 14:30"

        >>> format_timestamp(dt, "%d/%m/%Y")
        "25/12/2023"

    Note:
        For locale-aware formatting, use format_order_datetime() instead.
        This function uses Python's strftime(), not locale-specific formatting.
    """
    if not dt:
        return ""
    return dt.strftime(format_string)


def is_new(dt: datetime, days: int = 7) -> bool:
    """
    Check if a datetime is within the last N days.

    Useful for displaying "NEW" badges on recent items.

    Args:
        dt: DateTime object to check
        days: Number of days to consider as "new" (default: 7)

    Returns:
        True if the datetime is within the specified days, False otherwise

    Examples:
        >>> from datetime import datetime, timedelta, timezone
        >>> now = datetime.now(timezone.utc)

        >>> is_new(now - timedelta(days=3))
        True  # 3 days ago is "new"

        >>> is_new(now - timedelta(days=10))
        False  # 10 days ago is not "new"

        >>> is_new(now - timedelta(days=2), days=1)
        False  # 2 days ago is not "new" if threshold is 1 day

    Usage in Templates:
        {% if product.created_at|is_new %}
            <span class="badge">NEW</span>
        {% endif %}
    """
    if not dt:
        return False

    # Ensure timezone-aware datetime
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    diff = now - dt

    return diff.total_seconds() < (days * 86400)


def register_time_filters(app):
    """
    Register time utility functions as Jinja2 template filters.

    Usage in Templates:
        {{ order.created_at|time_ago }}
        {{ product.updated_at|format_timestamp }}
        {{ product.created_at|is_new }}

    Args:
        app: Flask application instance
    """
    app.jinja_env.filters['time_ago'] = time_ago
    app.jinja_env.filters['format_timestamp'] = format_timestamp
    app.jinja_env.filters['is_new'] = is_new
