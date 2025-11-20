"""Python convenience wrappers for the Rust naixi key encryptor."""

from typing import Final

from naixi_key_encryptor_native import (  # type: ignore[attr-defined]
    decrypt_naixi as _decrypt_naixi_native,
    encrypt_naixi as _encrypt_naixi_native,
    version as _native_version,
)

__all__ = ["encrypt_naixi", "decrypt_naixi", "version", "__version__"]


def encrypt_naixi(private_key: str, password: str) -> str:
    """Encrypt `private_key` with the supplied `password`."""
    return _encrypt_naixi_native(private_key, password)


def decrypt_naixi(ciphertext_hex: str, password: str) -> str:
    """Decrypt ciphertext produced by :func:`encrypt_naixi`."""
    return _decrypt_naixi_native(ciphertext_hex, password)


def version() -> str:
    """Return the Rust core version string."""
    return _native_version()


__version__: Final[str] = version()
