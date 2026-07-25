from cryptography.fernet import Fernet
from app.core.config import settings
import json
from typing import Any

# Ensure we have a valid key, default to a dev key if not provided
_fernet_key = settings.FERNET_SECRET_KEY.encode() if settings.FERNET_SECRET_KEY else Fernet.generate_key()
_cipher_suite = Fernet(_fernet_key)

def encrypt_data(data: Any) -> str:
    """
    Encrypts arbitrary JSON-serializable data.
    """
    if data is None:
        return None
    json_data = json.dumps(data)
    encrypted_bytes = _cipher_suite.encrypt(json_data.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")

def decrypt_data(encrypted_str: str) -> Any:
    """
    Decrypts a Fernet encrypted string back to its original JSON-serializable structure.
    """
    if not encrypted_str:
        return None
    try:
        decrypted_bytes = _cipher_suite.decrypt(encrypted_str.encode("utf-8"))
        return json.loads(decrypted_bytes.decode("utf-8"))
    except Exception:
        # Fallback for data that might not be encrypted yet
        try:
            return json.loads(encrypted_str)
        except:
            return encrypted_str
