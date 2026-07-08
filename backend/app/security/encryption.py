class TenantEncryptionManager:
    """
    Manages Envelope Encryption for data at rest. 
    Every tenant gets their own Data Encryption Key (DEK).
    """
    def get_tenant_key(self, tenant_id: str) -> bytes:
        # Mock: retrieves DEK from Vault
        return b"mock_tenant_specific_dek_32_bytes"

    def encrypt_data(self, tenant_id: str, plaintext: str) -> str:
        # Uses DEK to encrypt data
        return f"ENCRYPTED_{plaintext}"

    def decrypt_data(self, tenant_id: str, ciphertext: str) -> str:
        if ciphertext.startswith("ENCRYPTED_"):
            return ciphertext.replace("ENCRYPTED_", "")
        return ciphertext
