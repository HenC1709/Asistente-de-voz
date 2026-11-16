import re
import unicodedata


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    plain = "".join(c for c in decomposed if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^\w\s]", " ", plain).split())
