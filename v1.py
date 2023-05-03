import kubernetes
import os
import base64
from cryptography.fernet import Fernet


def encrypt_data(key, data):
    """Encrypt data using a symmetric encryption algorithm."""
    f = Fernet(key)
    return f.encrypt(data.encode('utf-8')).decode('utf-8')


def decrypt_data(key, data):
    """Decrypt data using a symmetric encryption algorithm."""
    f = Fernet(key)
    return f.decrypt(data.encode('utf-8')).decode('utf-8')


def create_secret(name, data, namespace):
    """Create a Kubernetes secret with the given name and data."""
    metadata = kubernetes.client.V1ObjectMeta(name=name)
    secret_data = {key: base64.b64encode(value.encode('utf-8')).decode('utf-8')
                   for key, value in data.items()}
    secret = kubernetes.client.V1Secret(
        api_version='v1',
        kind='Secret',
        metadata=metadata,
        type='Opaque',
        data=secret_data
    )
    api = kubernetes.client.CoreV1Api()
    api.create_namespaced_secret(namespace=namespace, body=secret)


def get_secret(name, namespace):
    """Retrieve a Kubernetes secret with the given name."""
    api = kubernetes.client.CoreV1Api()
    secret = api.read_namespaced_secret(name=name, namespace=namespace)
    return {key: base64.b64decode(value.encode('utf-8')).decode('utf-8')
            for key, value in secret.data.items()}


def main():
    # Load the encryption key from an environment variable
    key = os.environ.get('SECRET_ENCRYPTION_KEY')

    # Encrypt sensitive data
    encrypted_private_key = encrypt_data(key, 'my_private_key')
    encrypted_password = encrypt_data(key, 'my_password')

    # Create a Kubernetes secret with the encrypted data
    data = {
        'private_key': encrypted_private_key,
        'password': encrypted_password
    }
    create_secret('my-secret', data, 'my-namespace')

    # Retrieve the secret and decrypt the data
    secret_data = get_secret('my-secret', 'my-namespace')
    decrypted_private_key = decrypt_data(key, secret_data['private_key'])
    decrypted_password = decrypt_data(key, secret_data['password'])

    # Use the decrypted data for Web3 infrastructure
    # ...
