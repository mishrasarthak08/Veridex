from abc import ABC, abstractmethod

class BaseSecretProvider(ABC):
    @abstractmethod
    def get_secret(self, key: str) -> str:
        pass

class K8sSecretProvider(BaseSecretProvider):
    def get_secret(self, key: str) -> str:
        # Normally reads from /var/run/secrets/
        return "mock_k8s_secret"

class VaultSecretProvider(BaseSecretProvider):
    def get_secret(self, key: str) -> str:
        # Normally calls HashiCorp Vault API
        return "mock_vault_secret"
