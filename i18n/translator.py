import json
import os

class Translator:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Translator, cls).__new__(cls)
            cls._instance.translations = {}
            cls._instance.current_lang = "vi_VN"
            cls._instance.i18n_dir = os.path.dirname(os.path.abspath(__file__))
        return cls._instance

    def set_language(self, lang_code):
        self.current_lang = lang_code
        file_path = os.path.join(self.i18n_dir, f"{lang_code}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.translations = json.load(f)
            except Exception as e:
                print(f"Error loading translation {lang_code}: {e}")
        else:
            print(f"Translation file not found: {file_path}")

    def t(self, key, default=""):
        return self.translations.get(key, default if default else key)

# Global instances
translator = Translator()
