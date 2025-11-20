"""Python convenience wrappers for the Rust naixi key encryptor."""

from naixi_key_encryptor_native import decrypt_naixi, encrypt_naixi, version as _native_version  # type: ignore[attr-defined]

__all__ = ["encrypt_naixi", "decrypt_naixi", "version", "__version__"]


def version() -> str:
    """Return the Rust core version."""
    return _native_version()


__version__ = version()
