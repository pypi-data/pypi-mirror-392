"""
Locale selection and setup for Flask-I18N-Pro.

Implements a 4-tier locale selection strategy:
1. URL parameter (?lang=ru) - Highest priority, stores in session
2. Session (previously selected language)
3. Accept-Language header (browser preference)
4. Default (fallback to English)
"""

import logging
import os
import subprocess
from pathlib import Path

from flask import request, session
from flask_babel import Babel, refresh

logger = logging.getLogger(__name__)


def get_locale():
    """
    Determine the best locale for the current request.

    Returns:
        str: Selected language code (e.g., 'en', 'ru', 'mn', 'zh')

    Selection Priority:
        1. URL parameter: ?lang=ru
        2. Session: session['lang']
        3. Accept-Language header
        4. Default: 'en'

    Example:
        # User visits: /products?lang=ru
        # → Sets session['lang'] = 'ru'
        # → Returns 'ru'

        # Next visit without ?lang parameter
        # → Reads session['lang'] = 'ru'
        # → Returns 'ru'
    """
    from flask import current_app

    # 1. Check for language in URL args (highest priority)
    if "lang" in request.args:
        lang = request.args.get("lang")
        if lang in current_app.config.get("LANGUAGES", ["en"]):
            session["lang"] = lang
            logger.debug(f"Language set from URL parameter: {lang}")
            return lang

    # 2. Check for language in session
    if "lang" in session:
        lang = session.get("lang")
        logger.debug(f"Language from session: {lang}")
        return lang

    # 3. Use the browser's Accept-Language header
    languages = current_app.config.get("LANGUAGES", ["en"])
    best_match = request.accept_languages.best_match(languages)
    if best_match:
        logger.debug(f"Language from Accept-Language header: {best_match}")
        return best_match

    # 4. Default to English
    logger.debug("Falling back to default language 'en'")
    return "en"


def compile_translations(translations_dir=None):
    """
    Compile all translation files (.po → .mo).

    This should be run after updating translation files.
    Not required for runtime if .mo files already exist.

    Args:
        translations_dir: Path to translations directory (optional)

    Example:
        from flask_i18n_pro import compile_translations

        # On deploy or after updating translations
        compile_translations()

    Note:
        Requires pybabel to be installed:
        pip install babel
    """
    if translations_dir is None:
        # Try to find translations directory
        project_root = Path.cwd()
        translations_dir = project_root / "translations"

    translations_path = Path(translations_dir)

    if not translations_path.exists():
        logger.warning(f"Translations directory not found at {translations_path}")
        return False

    try:
        cmd = ["pybabel", "compile", "-d", str(translations_path)]
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("✅ Successfully compiled all translation files")

            # List .mo files to verify
            mo_files = list(translations_path.glob("*/LC_MESSAGES/messages.mo"))
            logger.info(f"Found {len(mo_files)} .mo files")
            return True
        else:
            logger.warning(f"Translation compilation had issues: {result.stderr}")
            return False

    except (OSError, subprocess.SubprocessError) as e:
        logger.warning(f"Error compiling translations: {e}")
        return False


def setup_i18n(app, config=None):
    """
    Initialize Flask-I18N-Pro with automatic locale selection.

    Args:
        app: Flask application instance
        config: Optional configuration dict

    Configuration Options:
        LANGUAGES: List of supported language codes (default: ['en'])
        BABEL_DEFAULT_LOCALE: Default locale (default: 'en')
        BABEL_DEFAULT_TIMEZONE: Default timezone (default: 'UTC')
        BABEL_TRANSLATION_DIRECTORIES: Path to translations (default: './translations')
        BABEL_REFRESH_EVERY_REQUEST: Refresh in dev mode (default: False)

    Returns:
        Babel instance

    Example:
        from flask import Flask
        from flask_i18n_pro import setup_i18n

        app = Flask(__name__)
        app.config['LANGUAGES'] = ['en', 'ru', 'mn', 'zh']
        app.config['BABEL_DEFAULT_LOCALE'] = 'en'

        babel = setup_i18n(app)

        # Locale is now automatically selected per request!

    Directory Structure:
        your_app/
        ├── app.py
        └── translations/
            ├── en/
            │   └── LC_MESSAGES/
            │       ├── messages.po
            │       └── messages.mo
            ├── ru/
            │   └── LC_MESSAGES/
            │       ├── messages.po
            │       └── messages.mo
            └── mn/
                └── LC_MESSAGES/
                    ├── messages.po
                    └── messages.mo
    """
    # Set default configuration
    if not config:
        config = {}

    # Default supported languages
    if 'LANGUAGES' not in app.config:
        app.config['LANGUAGES'] = config.get('LANGUAGES', ['en'])

    # Get translations directory
    if 'BABEL_TRANSLATION_DIRECTORIES' not in app.config:
        project_root = config.get('project_root', os.getcwd())
        translations_path = os.path.join(project_root, "translations")
        app.config['BABEL_TRANSLATION_DIRECTORIES'] = translations_path
    else:
        translations_path = app.config['BABEL_TRANSLATION_DIRECTORIES']

    # Set Babel configuration
    app.config.setdefault('BABEL_DEFAULT_LOCALE', 'en')
    app.config.setdefault('BABEL_DEFAULT_TIMEZONE', 'UTC')
    app.config.setdefault('BABEL_REFRESH_EVERY_REQUEST', app.config.get('DEBUG', False))

    logger.info(f"Translations directory: {translations_path}")

    # Check if translations directory exists
    if not os.path.exists(translations_path):
        logger.warning(
            f"Translations directory not found at {translations_path}. "
            f"Create it with: pybabel init -i messages.pot -d translations -l en"
        )

    # Initialize Babel with locale selector
    babel = Babel()
    babel.init_app(app, locale_selector=get_locale)

    # Add before_request handler to refresh translations in dev mode
    @app.before_request
    def refresh_translations():
        if app.config.get('BABEL_REFRESH_EVERY_REQUEST', False):
            refresh()

    # Register template filters
    from .formatters import register_filters
    register_filters(app)

    from .time_utils import register_time_filters
    register_time_filters(app)

    logger.info(f"Flask-I18N-Pro initialized with languages: {app.config['LANGUAGES']}")

    return babel
