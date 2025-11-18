import requests
from dataclasses import dataclass

@dataclass
class TranslationResult:
    text: str
    from_lang: str
    to_lang: str

class IndigeTranslate:
    """
    API de traducciones indígenas.
    """
    def __init__(self, token: str, base_url: str = "https://wintranslated.onrender.com/api"):
        self.token = token
        self.base_url = base_url

    def translate(self, text: str, source: str, target: str) -> TranslationResult:
        endpoint = f"{self.base_url}/translate"

        headers = {
            "win-api-token": self.token,
            "Content-Type": "application/json"
        }

        payload = {
            "text": text,
            "from": source,
            "to": target
        }

        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        return TranslationResult(
            text=data.get("translated"),
            from_lang=data.get("from", source),
            to_lang=data.get("to", target)
        )