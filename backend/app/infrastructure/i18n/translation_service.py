"""Translation service for i18n."""
from typing import Dict, Optional
import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TranslationService:
    """Service for translating system messages."""
    
    def __init__(self, translations_dir: Optional[str] = None):
        if translations_dir is None:
            translations_dir = os.path.join(
                os.path.dirname(__file__), "translations"
            )
        self.translations_dir = Path(translations_dir)
        self._translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()
    
    def _load_translations(self):
        """Load translation files."""
        if not self.translations_dir.exists():
            logger.warning(f"Translations directory not found: {self.translations_dir}")
            return
        
        for lang_file in self.translations_dir.glob("*.json"):
            lang = lang_file.stem
            try:
                with open(lang_file, "r", encoding="utf-8") as f:
                    self._translations[lang] = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load {lang_file}: {e}")
    
    def translate(self, key: str, language: str, **params) -> str:
        """
        Translate a key to the specified language.
        
        Implements BR-014: Language fallback
        Priority: 1. Requested language, 2. English, 3. Key itself
        """
        # Try requested language
        if language in self._translations:
            if key in self._translations[language]:
                try:
                    return self._translations[language][key].format(**params)
                except KeyError:
                    # Missing parameter, return as-is
                    return self._translations[language][key]
        
        # Fallback to English
        if "en" in self._translations and key in self._translations["en"]:
            try:
                return self._translations["en"][key].format(**params)
            except KeyError:
                return self._translations["en"][key]
        
        # Last resort
        logger.warning(f"Missing translation: {key} for {language}")
        return key
