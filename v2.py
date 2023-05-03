import base64
import os
import subprocess

from kubernetes import client, config
from cryptography.fernet import Fernet


def generate_key():
    """Generates a new Fernet key."""
    return Fernet.generate_key()


def encrypt_data(data, key):
    """Encrypts the data with the given key."""
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data


def decrypt_data(encrypted_data, key):
    """Decrypts the encrypted data with the given key."""
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data).decode()
    return decrypted_data


def create_secret(secret_name, data, namespace):
    """Creates a Kubernetes secret with the given name and data in the specified namespace."""
    api_instance = client.CoreV1Api()
    body = {"apiVersion": "v1", "kind": "Secret", "metadata": {"name": secret_name}, "data": data}
    api_instance.create_namespaced_secret(namespace, body)


def get_secret(secret_name, namespace):
    """Retrieves the data stored in the specified Kubernetes secret."""
    api_instance = client.CoreV1Api()
    secret = api_instance.read_namespaced_secret(secret_name, namespace)
    return secret.data


def get_key():
    """Retrieves the Fernet key stored in the environment variable."""
    key = os.environ.get("FERNET_KEY")
    if not key:
        key = generate_key()
        os.environ["FERNET_KEY"] = key.decode()
    return key


def encrypt_and_store_data(data, secret_name, namespace):
    """Encrypts the data, stores it in a Kubernetes secret, and returns the encrypted data."""
    key = get_key()
    encrypted_data = encrypt_data(data, key)
    encoded_data = base64.b64encode(encrypted_data).decode()
    create_secret(secret_name, {"encrypted_data": encoded_data}, namespace)
    return encrypted_data


def get_decrypted_data(secret_name, namespace):
    """Retrieves the encrypted data from the Kubernetes secret, decrypts it, and returns the decrypted data."""
    encoded_data = get_secret(secret_name, namespace)["encrypted_data"]
    encrypted_data = base64.b64decode(encoded_data.encode())
    key = get_key()
    decrypted_data = decrypt_data(encrypted_data, key)
    return decrypted_data


def set_access_control_policy(secret_name, namespace):
    """Sets the access control policy for the specified Kubernetes secret."""
    subprocess.run(["kubectl", "create", "role", f"{secret_name}-role", f"--verb=get", f"--verb=list", f"--verb=watch", f"--resource=secrets", f"--resource-name={secret_name}", f"--namespace={namespace}"], check=True)
    subprocess.run(["kubectl", "create", "rolebinding", f"{secret_name}-rolebinding", f"--role={secret_name}-role", f"--serviceaccount={namespace}:default", f"--namespace={namespace}"], check=True)


def main():
    # Load the Kubernetes configuration from the default location.
    config.load_kube_config()

    # Set the namespace and secret name.
    namespace = "default"
    secret_name = "my-secret"

    # Get the sensitive information from the user.
    data = input("Enter the sensitive information: ")

    # Encrypt the data and store it in a Kubernetes secret.
    encrypted_data = encrypt_and_store_data(data, secret_name, namespace)
    print("Encrypted data:", encrypted_data)

    # Get the decrypted data from
