"""Post-quantum cryptographic family: PQ-ML-KEM-1024-ML-DSA-87

This family provides high security (AES-256 equivalent) post-quantum cryptography
by bundling:
- ML-KEM-1024 for key encapsulation (encryption)
- ML-DSA-87 for digital signatures

Security Level: 5 (NIST Level 5 - highest standardized level)
Key Sizes:
  - Public: 4,160 bytes (KEM 1,568 + Sig 2,592)
  - Private: 8,064 bytes (KEM 3,168 + Sig 4,896)
"""

from .._libboqs import (
    PQFamilyConfig,
    generate_bundled_keys,
    check_bundled_key_pair,
    encrypt_hybrid,
    decrypt_hybrid,
    sign_data,
    verify_data_signature,
)

FAMILY_NAME = "PQ-ML-KEM-1024-ML-DSA-87"

# Configuration for this family
_CONFIG = PQFamilyConfig(
    kem_algorithm="ML-KEM-1024",
    sig_algorithm="ML-DSA-87",
    kem_public_size=1568,
    kem_private_size=3168,
    kem_ciphertext_size=1568,
    sig_public_size=2592,
    sig_private_size=4896,
)

# Supported options
ENCRYPTION_OPTIONS = [
    "AES-256-GCM",
    "AES-128-GCM",
    "ChaCha20-Poly1305",
]

SIGNATURE_OPTIONS = [
    "direct",
    "prehash-SHA256",
    "prehash-SHA512",
]

DEFAULT_ENCRYPTION_OPTION = "AES-256-GCM"
DEFAULT_SIGNATURE_OPTION = "direct"


def generate_keys(keylength: int = None, **kwargs) -> tuple[bytes, bytes]:
    """Generate a bundled keypair for PQ-ML-KEM-1024-ML-DSA-87.

    Note: Post-quantum algorithms have fixed key sizes. The keylength parameter
    is accepted for API compatibility but ignored.

    Args:
        keylength: Ignored (post-quantum algorithms use fixed key sizes)
        **kwargs: Additional arguments (ignored)

    Returns:
        tuple: (public_key_bundle, private_key_bundle) as bytes
            - public_key_bundle: 4,160 bytes (KEM public 1,568 + Sig public 2,592)
            - private_key_bundle: 8,064 bytes (KEM private 3,168 + Sig private 4,896)
    """
    return generate_bundled_keys(_CONFIG)


def verify_key_pair(private_key: bytes, public_key: bytes) -> bool:
    """Check if a private key and public key form a valid keypair.

    Args:
        private_key: Private key bundle (8,064 bytes)
        public_key: Public key bundle (4,160 bytes)

    Returns:
        bool: True if the keys form a valid pair, False otherwise
    """
    return check_bundled_key_pair(private_key, public_key, _CONFIG)


def encrypt(
    data_to_encrypt: bytes, public_key: bytes, encryption_options: str = None
) -> bytes:
    """Encrypt data using hybrid KEM/DEM encryption.

    Args:
        data_to_encrypt: Plaintext data to encrypt
        public_key: Public key bundle (4,160 bytes)
        encryption_options: Symmetric cipher to use (default: "AES-256-GCM")

    Returns:
        bytes: Encrypted data (KEM ciphertext + nonce + symmetric ciphertext + tag)

    Raises:
        EncryptionOptionError: If encryption_options is not supported
    """
    if not encryption_options:
        encryption_options = DEFAULT_ENCRYPTION_OPTION

    return encrypt_hybrid(
        data_to_encrypt, public_key, _CONFIG, encryption_options
    )


def decrypt(
    data_to_decrypt: bytes, private_key: bytes, encryption_options: str = None
) -> bytes:
    """Decrypt data using hybrid KEM/DEM decryption.

    Args:
        data_to_decrypt: Encrypted data
        private_key: Private key bundle (12,224 bytes)
        encryption_options: Symmetric cipher to use (must match encryption)

    Returns:
        bytes: Decrypted plaintext data

    Raises:
        EncryptionOptionError: If encryption_options is not supported
        ValueError: If decryption fails
    """
    if not encryption_options:
        encryption_options = DEFAULT_ENCRYPTION_OPTION

    return decrypt_hybrid(
        data_to_decrypt, private_key, _CONFIG, encryption_options
    )


def sign(
    data: bytes, private_key: bytes, signature_options: str = None
) -> bytes:
    """Sign data using ML-DSA-87.

    Args:
        data: Data to sign
        private_key: Private key bundle (12,224 bytes)
        signature_options: Signature protocol (default: "direct")

    Returns:
        bytes: Digital signature (max 4,627 bytes)

    Raises:
        SignatureOptionError: If signature_options is not supported
    """
    if not signature_options:
        signature_options = DEFAULT_SIGNATURE_OPTION

    return sign_data(data, private_key, _CONFIG, signature_options)


def verify_signature(
    signature: bytes,
    data: bytes,
    public_key: bytes,
    signature_options: str = None,
) -> bool:
    """Verify a signature using ML-DSA-87.

    Args:
        signature: Signature to verify
        data: Original data that was signed
        public_key: Public key bundle (4,160 bytes)
        signature_options: Signature protocol (must match signing)

    Returns:
        bool: True if signature is valid, False otherwise

    Raises:
        SignatureOptionError: If signature_options is not supported
    """
    if not signature_options:
        signature_options = DEFAULT_SIGNATURE_OPTION

    return verify_data_signature(
        signature, data, public_key, _CONFIG, signature_options
    )


def get_encrytpion_options() -> list:
    """Get the encryption options supported by this family.

    Returns:
        list: Supported encryption options
    """
    return ENCRYPTION_OPTIONS


def get_signature_options() -> list:
    """Get the signature options supported by this family.

    Returns:
        list: Supported signature options
    """
    return SIGNATURE_OPTIONS
