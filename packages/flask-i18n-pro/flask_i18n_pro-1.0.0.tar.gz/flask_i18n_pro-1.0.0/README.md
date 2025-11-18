# Flask-I18N-Pro

Internationalization for Flask with Cyrillic and Asian language support.

## What it does

- **4-tier locale selection**: URL parameter → Session → Accept-Language header → Default
- **Cyrillic-aware formatting**: Russian number formatting (1 234,56 instead of 1,234.56)
- **Proper pluralization**: Handles complex rules (Russian: 1/2-4/5+ forms)
- **Context-aware translations**: Disambiguate homonyms
- **Time-ago utilities**: "2 hours ago" with correct plurals

Built while working on [wallmarkets](https://wallmarkets.store). Tested with English, Russian, Mongolian, Chinese.

## Installation

```bash
pip install flask-i18n-pro
```

## Usage

### Basic setup

```python
from flask import Flask
from flask_i18n_pro import setup_i18n

app = Flask(__name__)
app.config['LANGUAGES'] = ['en', 'ru', 'mn', 'zh']

setup_i18n(app)
# Locale now auto-selected per request
```

### Formatting in templates

```jinja2
{# Date/time #}
{{ order.created_at|format_order_datetime }}
{# en: "Dec 25, 2023, 2:30 PM" #}
{# ru: "25 дек. 2023 г., 14:30" #}

{# Price - Cyrillic formatting #}
{{ product.price|format_price('RUB') }}
{# en: "RUB 15,000.00" #}
{# ru: "15 000,00 ₽" (space separator!) #}

{# Time ago #}
{{ comment.created_at|time_ago }}
{# en: "2 minutes ago" #}
{# ru: "2 минуты назад" #}
```

### Cyrillic number formatting

This is the main difference from Flask-Babel:

```python
from flask_i18n_pro import format_weight

# With Russian locale
format_weight(1234.5)  # → "1 234,5"
# Not "1,234.5" like Flask-Babel does
```

## Locale selection

Automatic 4-tier fallback:

1. `?lang=ru` URL parameter → saves to session
2. `session['lang']` if previously set
3. `Accept-Language` header from browser
4. Default configured language

## Configuration

```python
app.config['LANGUAGES'] = ['en', 'ru', 'mn', 'zh']
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
```

## License

MIT

## Contributing

Pull requests welcome. Please add tests.
