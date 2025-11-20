"Crypto utility dealing with encryption and decryption"

import base64
import os
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from aixtools.utils.config_util import read_from_text_file


class AesGcmCrypto:
    """AES GCM Crypto utility"""

    # Default for normal development
    CRYPTO_KEY_FILE = os.getenv("AIXTOOLS_CRYPTO_KEY_FILE", ".aixtools-crypto.key")
    CRYPTO_KEY_PATH = os.path.expanduser(f"~/{CRYPTO_KEY_FILE}")

    def __init__(self, b64key: str):
        self.key = base64.b64decode(b64key)
        if len(self.key) not in (16, 24, 32):
            raise ValueError("Invalid AES key length (must be 128, 192, or 256 bits)")
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext using AES-GCM"""
        nonce = os.urandom(12)  # 96-bit nonce as required by AESGCM
        ct = self.aesgcm.encrypt(nonce, plaintext.encode(), None)
        return base64.b64encode(nonce + ct).decode()

    def decrypt(self, b64token: str) -> str | None:
        """Decrypt plaintext using AES-GCM"""
        if not b64token:
            return None
        data = base64.b64decode(b64token)
        nonce, cipher_text = data[:12], data[12:]
        return self.aesgcm.decrypt(nonce, cipher_text, None).decode()

    @classmethod
    def create(cls):
        """Create AES GCM Crypto utility"""
        return cls(read_from_text_file(Path(cls.CRYPTO_KEY_PATH)))
