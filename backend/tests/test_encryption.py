import pytest
from app.core.encryption import encrypt_data, decrypt_data, _cipher_suite
import json

def test_aes_gcm_encryption():
    data = {"api_key": "sk-12345", "tenant_id": "test-tenant"}
    encrypted = encrypt_data(data)
    
    # Verify it has the v2$ prefix
    assert encrypted.startswith("v2$")
    
    # Verify it can be decrypted back
    decrypted = decrypt_data(encrypted)
    assert decrypted == data

def test_fernet_fallback():
    data = {"legacy_key": "old-key-data"}
    # Encrypt using the legacy fernet cipher directly
    legacy_encrypted = _cipher_suite.encrypt(json.dumps(data).encode("utf-8")).decode("utf-8")
    
    # It shouldn't have v2$
    assert not legacy_encrypted.startswith("v2$")
    
    # It should decrypt correctly using the fallback in decrypt_data
    decrypted = decrypt_data(legacy_encrypted)
    assert decrypted == data

def test_none_values():
    assert encrypt_data(None) is None
    assert decrypt_data(None) is None

def test_unencrypted_fallback():
    # If a string isn't encrypted (plain json), decrypt_data falls back to json.loads or returns the string
    data = {"some": "data"}
    json_str = json.dumps(data)
    assert decrypt_data(json_str) == data
    
    plain_str = "just a string"
    assert decrypt_data(plain_str) == plain_str
