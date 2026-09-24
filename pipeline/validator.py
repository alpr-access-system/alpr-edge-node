import re

def validate_plate(text):
    """
    Valida si el texto coincide con un formato de patente chilena válido.
    """
    # Formato antiguo (ej. AB1234) o nuevo (ej. ABCD12)
    # Esta es una validación simplificada
    text = text.replace(" ", "").upper()
    return bool(re.match(r'^[A-Z]{2}\d{4}$|^[A-Z]{4}\d{2}$', text))
