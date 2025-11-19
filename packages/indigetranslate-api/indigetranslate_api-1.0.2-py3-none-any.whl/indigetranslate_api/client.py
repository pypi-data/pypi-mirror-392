import requests
from dataclasses import dataclass

@dataclass
class TranslationResult:
    text: str
    from_lang: str
    to_lang: str

class IndigeTranslateError(Exception):
    def __init__(self, message: str, status_code: int = None, server_message: str = None):
        self.message = message
        self.status_code = status_code
        self.server_message = server_message
        super().__init__(self.message)

class InvalidLanguageCodeError(IndigeTranslateError):
    pass

class InvalidLanguageCombinationError(IndigeTranslateError):
    pass

class IndigeTranslate:
    SUPPORTED_LANGUAGES = {
        "tnk": "Tenek",
        "nhe": "Náhuatl",
        "yua": "Maya",
        "es": "Español"
    }

    def __init__(self, token: str, base_url: str = "https://wintranslated.onrender.com/api"):
        self.token = token
        self.base_url = base_url

    @classmethod
    def get_supported_languages(cls):
        return cls.SUPPORTED_LANGUAGES.copy()

    def _validate_language_code(self, code: str):
        if code not in self.SUPPORTED_LANGUAGES:
            raise InvalidLanguageCodeError(
                f"Código de idioma no válido: '{code}'. "
                f"Códigos soportados: {', '.join(self.SUPPORTED_LANGUAGES.keys())}. "
                f"Usa get_supported_languages() para ver los idiomas disponibles."
            )

    def _validate_language_combination(self, source: str, target: str):
        if source == target:
            raise InvalidLanguageCombinationError(
                f"El idioma origen y destino no pueden ser iguales: '{source}'"
            )

        if "tnk" in [source, target]:
            if "es" not in [source, target]:
                raise InvalidLanguageCombinationError(
                    "El idioma 'tnk' (Tenek) solo puede traducirse desde o hacia 'es' (Español)"
                )

        if (source == "nhe" and target == "yua") or (source == "yua" and target == "nhe"):
            raise InvalidLanguageCombinationError(
                "No se puede traducir entre 'nhe' (Náhuatl) y 'yua' (Maya). "
                "Ambos solo son bidireccionales con 'es' (Español)"
            )

    def translate(self, text: str, source: str, target: str) -> TranslationResult:
        source = source.lower()
        target = target.lower()

        self._validate_language_code(source)
        self._validate_language_code(target)
        self._validate_language_combination(source, target)

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

        try:
            response = requests.post(endpoint, json=payload, headers=headers)
            
            if response.status_code != 200:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    pass
                
                server_message = error_data.get("error") or error_data.get("message") or response.text
                raise IndigeTranslateError(
                    f"Error del servidor (código {response.status_code}): {server_message}",
                    status_code=response.status_code,
                    server_message=server_message
                )

            data = response.json()

            if "translated" not in data:
                raise IndigeTranslateError(
                    "La respuesta del servidor no contiene el campo 'translated'",
                    status_code=response.status_code
                )

            return TranslationResult(
                text=data.get("translated"),
                from_lang=data.get("from", source),
                to_lang=data.get("to", target)
            )

        except IndigeTranslateError:
            raise
        except requests.exceptions.RequestException as e:
            raise IndigeTranslateError(
                f"Error de conexión: {str(e)}"
            )
        except Exception as e:
            raise IndigeTranslateError(
                f"Error inesperado: {str(e)}"
            )