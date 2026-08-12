from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.core.config import settings
import json
import os
import base64
import hashlib
from typing import Any

# Ensure we have a valid key, default to a dev key if not provided
_raw_key = settings.FERNET_SECRET_KEY.encode() if settings.FERNET_SECRET_KEY else Fernet.generate_key()
# We keep Fernet for legacy fallback
_cipher_suite = Fernet(_raw_key)

# We derive a 32-byte (256-bit) key for AESGCM using SHA-256 on the raw key
_aes_key = hashlib.sha256(_raw_key).digest()
_aesgcm = AESGCM(_aes_key)

def encrypt_data(data: Any) -> str:
    """
    Encrypts arbitrary JSON-serializable data using AES-256-GCM.
    Returns: v2$<base64-encoded-nonce>$<base64-encoded-ciphertext>
    """
    if data is None:
        return None
    json_data = json.dumps(data)
    
    # Generate a random 12-byte nonce
    nonce = os.urandom(12)
    # Encrypt (the auth tag is automatically appended to the ciphertext in AESGCM)
    ciphertext = _aesgcm.encrypt(nonce, json_data.encode("utf-8"), None)
    
    encoded_nonce = base64.b64encode(nonce).decode("utf-8")
    encoded_ciphertext = base64.b64encode(ciphertext).decode("utf-8")
    
    return f"v2${encoded_nonce}${encoded_ciphertext}"

def decrypt_data(encrypted_str: str) -> Any:
    """
    Decrypts an encrypted string back to its original JSON-serializable structure.
    Handles both AES-256-GCM (v2$) and Fernet (legacy) formats.
    """
    if not encrypted_str:
        return None
        
    try:
        if encrypted_str.startswith("v2$"):
            # AES-256-GCM
            _, encoded_nonce, encoded_ciphertext = encrypted_str.split("$", 2)
            nonce = base64.b64decode(encoded_nonce)
            ciphertext = base64.b64decode(encoded_ciphertext)
            
            decrypted_bytes = _aesgcm.decrypt(nonce, ciphertext, None)
            return json.loads(decrypted_bytes.decode("utf-8"))
        else:
            # Legacy Fernet fallback
            decrypted_bytes = _cipher_suite.decrypt(encrypted_str.encode("utf-8"))
            return json.loads(decrypted_bytes.decode("utf-8"))
    except Exception:
        # Fallback for data that might not be encrypted yet
        try:
            return json.loads(encrypted_str)
        except:
            return encrypted_str
