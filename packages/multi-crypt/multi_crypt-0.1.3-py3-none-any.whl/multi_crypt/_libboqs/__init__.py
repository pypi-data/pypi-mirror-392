"""
liboqs integration machinery for post-quantum cryptographic families.

This module provides shared utilities for implementing post-quantum algorithm
families using the liboqs library. It handles key bundling, hybrid encryption
(KEM/DEM), and signature operations.
"""

from .pq_base import (
    PQFamilyConfig,
    generate_bundled_keys,
    check_bundled_key_pair,
    encrypt_hybrid,
    decrypt_hybrid,
    sign_data,
    verify_data_signature,
)

__all__ = [
    "PQFamilyConfig",
    "generate_bundled_keys",
    "check_bundled_key_pair",
    "encrypt_hybrid",
    "decrypt_hybrid",
    "sign_data",
    "verify_data_signature",
]
