"""
Template rendering logic using Jinja2.

This module handles:
- Loading i18n translations
- Rendering templates with translation strings
- Providing helper functions for templates
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from importlib import resources
from jinja2 import Environment, PackageLoader, select_autoescape, TemplateNotFound


class TemplateRenderer:
    """
    Renders Jinja2 templates with i18n support.

    Responsibilities:
    1. Load translation files (en.json, ko.json)
    2. Set up Jinja2 environment
    3. Render templates with translation context
    4. Provide helper functions to templates
    """

    def __init__(self, lang: str = 'en'):
        """
        Initialize the template renderer.

        Args:
            lang: Language code ('en' or 'ko')
        """
        self.lang = lang
        self.translations = self._load_translations(lang)

        # Set up Jinja2 environment
        self.env = Environment(
            loader=PackageLoader('purposely', 'templates/source'),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )

        # Add helper functions
        self._register_filters()

    def _load_translations(self, lang: str) -> Dict[str, Any]:
        """
        Load translation file for the specified language.

        Args:
            lang: Language code

        Returns:
            Dictionary containing all translation strings

        Raises:
            FileNotFoundError: If translation file doesn't exist
        """
        try:
            # Use importlib.resources for Python 3.10+
            i18n_package = resources.files('purposely') / 'i18n'
            translation_file = i18n_package / f'{lang}.json'

            # Read and parse JSON
            content = translation_file.read_text(encoding='utf-8')
            return json.loads(content)
        except FileNotFoundError:
            raise FileNotFoundError(f"Translation file not found for language: {lang}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in translation file {lang}.json: {e}")

    def _register_filters(self):
        """
        Register custom Jinja2 filters and functions.
        """
        def now_filter(value, timezone='utc', format='%Y-%m-%d'):
            """Return current date/time in specified format. Value is ignored."""
            from datetime import timezone as tz
            return datetime.now(tz.utc).strftime(format) if timezone == 'utc' else datetime.now().strftime(format)

        self.env.filters['now'] = now_filter

    def render(self, template_name: str, **context) -> str:
        """
        Render a template with the given context.

        Templates use i18n translations via the 't' variable.

        Args:
            template_name: Name of the template file (e.g., 'GLOBAL_PURPOSE.md')
            **context: Additional context variables

        Returns:
            Rendered template as string

        Raises:
            TemplateNotFound: If template doesn't exist
        """
        try:
            template = self.env.get_template(template_name)
        except TemplateNotFound:
            raise FileNotFoundError(f"Template not found: {template_name}")

        # Merge translations and context
        render_context = {
            't': self.translations,
            'lang': self.lang,
            **context
        }

        return template.render(**render_context)

    def render_to_file(self, template_name: str, output_path: Path, **context):
        """
        Render a template and write to file.

        Args:
            template_name: Name of the template file
            output_path: Path where the rendered content will be written
            **context: Additional context variables
        """
        content = self.render(template_name, **context)

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
