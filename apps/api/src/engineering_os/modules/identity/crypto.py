"""Encryption of third-party tokens at rest (BR-02).

GitHub access tokens are live, `repo`-scoped credentials; a database dump must not expose them. Tokens
are encrypted before they touch a column and decrypted only at the point of use. In production
`TOKEN_ENCRYPTION_KEY` must be set; without it a deterministic insecure dev key is used and a warning
is logged — but tokens are never stored as plaintext, in any environment."""
import base64
import hashlib
import logging
from typing import Optional

from cryptography.fernet import Fernet

from ...config import settings

logger = logging.getLogger("eos.security")

_DEV_KEY_MATERIAL = "engineering-os-insecure-dev-key"  # used only when TOKEN_ENCRYPTION_KEY is unset


def _fernet(key_material: str) -> Fernet:
    # Derive a valid 32-byte url-safe Fernet key from arbitrary key material.
    digest = hashlib.sha256(key_material.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


class TokenCipher:
    def __init__(self, key: str = "") -> None:
        self.secure = bool(key)
        self._fernet = _fernet(key) if key else _fernet(_DEV_KEY_MATERIAL)

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, token: str) -> str:
        return self._fernet.decrypt(token.encode("utf-8")).decode("utf-8")


_cipher: Optional[TokenCipher] = None


def get_token_cipher() -> TokenCipher:
    """Process-wide cipher, built once. Warns once if running on the insecure dev key."""
    global _cipher
    if _cipher is None:
        _cipher = TokenCipher(settings.token_encryption_key)
        if not _cipher.secure:
            logger.warning(
                "TOKEN_ENCRYPTION_KEY is not set — encrypting tokens with an insecure dev key. "
                "Set TOKEN_ENCRYPTION_KEY in production."
            )
    return _cipher
