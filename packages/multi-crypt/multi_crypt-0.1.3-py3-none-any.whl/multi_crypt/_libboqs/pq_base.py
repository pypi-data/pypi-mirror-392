"""
Base implementation for post-quantum cryptographic families using liboqs.

This module provides the core functionality for bundled hybrid post-quantum
cryptographic operations combining Key Encapsulation Mechanisms (KEM) with
Digital Signature Algorithms (DSA).
"""

import hashlib
from dataclasses import dataclass

try:
    import oqs
except ImportError:
    raise ImportError(
        "liboqs-python is required for post-quantum cryptography. "
        "Install it with: pip install liboqs-python"
    )

try:
    from Crypto.Cipher import AES
except ImportError:
    raise ImportError(
        "pycryptodome is required for hybrid encryption. "
        "Install it with: pip install pycryptodome"
    )

from ..errors import EncryptionOptionError, SignatureOptionError


@dataclass
class PQFamilyConfig:
    """Configuration for a post-quantum hybrid cryptographic family.

    Attributes:
        kem_algorithm: The KEM algorithm name (e.g., "ML-KEM-768")
        sig_algorithm: The signature algorithm name (e.g., "ML-DSA-65")
        kem_public_size: Size of KEM public key in bytes
        kem_private_size: Size of KEM private key in bytes
        kem_ciphertext_size: Size of KEM ciphertext in bytes
        sig_public_size: Size of signature public key in bytes
        sig_private_size: Size of signature private key in bytes
    """

    kem_algorithm: str
    sig_algorithm: str
    kem_public_size: int
    kem_private_size: int
    kem_ciphertext_size: int
    sig_public_size: int
    sig_private_size: int

    @property
    def public_bundle_size(self) -> int:
        """Total size of bundled public key."""
        return self.kem_public_size + self.sig_public_size

    @property
    def private_bundle_size(self) -> int:
        """Total size of bundled private key."""
        return self.kem_private_size + self.sig_private_size


def generate_bundled_keys(config: PQFamilyConfig) -> tuple[bytes, bytes]:
    """Generate a bundled keypair containing both KEM and signature keys.

    Args:
        config: Family configuration specifying algorithms and key sizes

    Returns:
        tuple: (public_key_bundle, private_key_bundle) as bytes

    Format:
        - public_bundle: kem_public || sig_public
        - private_bundle: kem_private || sig_private
    """
    # Generate KEM keypair
    with oqs.KeyEncapsulation(config.kem_algorithm) as kem:
        kem_public = kem.generate_keypair()
        kem_private = kem.export_secret_key()

    # Generate signature keypair
    with oqs.Signature(config.sig_algorithm) as signer:
        sig_public = signer.generate_keypair()
        sig_private = signer.export_secret_key()

    assert len(kem_public) == config.kem_public_size, (
        "key generation: unexpected size for kem public key"
    )
    assert len(kem_private) == config.kem_private_size, (
        "key generation: unexpected size for kem private key"
    )
    assert len(sig_public) == config.sig_public_size, (
        "key generation: unexpected size for sig public key"
    )
    assert len(sig_private) == config.sig_private_size, (
        "key generation: unexpected size for sig private key"
    )

    # Bundle keys
    public_bundle = kem_public + sig_public
    private_bundle = kem_private + sig_private

    return (public_bundle, private_bundle)


def check_bundled_key_pair(
    private_bundle: bytes, public_bundle: bytes, config: PQFamilyConfig
) -> bool:
    """Check if a private key bundle and public key bundle form a valid keypair.

    Note: For post-quantum algorithms, we cannot derive public keys from private keys.
    Instead, we verify the keypair by performing a test encryption/decryption cycle.

    Args:
        private_bundle: Bundled private key bytes (kem_private || sig_private)
        public_bundle: Bundled public key bytes (kem_public || sig_public)
        config: Family configuration

    Returns:
        bool: True if the keys form a valid pair, False otherwise
    """
    try:
        # Verify bundle sizes
        if len(private_bundle) != config.private_bundle_size:
            return False
        if len(public_bundle) != config.public_bundle_size:
            return False

        # Extract KEM keys
        kem_public = public_bundle[0 : config.kem_public_size]
        kem_private = private_bundle[0 : config.kem_private_size]

        # Test KEM keypair by doing encapsulation/decapsulation
        with oqs.KeyEncapsulation(config.kem_algorithm) as kem:
            kem_ciphertext, shared_secret_1 = kem.encap_secret(kem_public)

        with oqs.KeyEncapsulation(
            config.kem_algorithm, secret_key=kem_private
        ) as kem:
            shared_secret_2 = kem.decap_secret(kem_ciphertext)

        # If decapsulation produces the same shared secret, the KEM keypair is valid
        if shared_secret_1 != shared_secret_2:
            return False

        # Extract signature keys
        sig_public = public_bundle[config.kem_public_size :]
        sig_private_start = config.kem_private_size
        sig_private = private_bundle[
            sig_private_start : sig_private_start + config.sig_private_size
        ]

        # Test signature keypair by signing and verifying test data
        test_data = b"MultiCrypt key pair verification test"
        with oqs.Signature(
            config.sig_algorithm, secret_key=sig_private
        ) as signer:
            signature = signer.sign(test_data)

        with oqs.Signature(config.sig_algorithm) as verifier:
            is_valid = verifier.verify(test_data, signature, sig_public)

        return is_valid

    except Exception:
        return False


def encrypt_hybrid(
    data: bytes,
    public_bundle: bytes,
    config: PQFamilyConfig,
    encryption_option: str = "AES-256-GCM",
) -> bytes:
    """Encrypt data using hybrid KEM/DEM encryption.

    The process:
    1. Extract KEM public key from bundle
    2. Use KEM to encapsulate a shared secret
    3. Encrypt data with shared secret using symmetric cipher
    4. Return: kem_ciphertext || nonce || symmetric_ciphertext || tag

    Args:
        data: Plaintext data to encrypt
        public_bundle: Bundled public key containing KEM public key
        config: Family configuration
        encryption_option: Symmetric cipher to use ("AES-256-GCM", "AES-128-GCM", "ChaCha20-Poly1305")

    Returns:
        bytes: Encrypted data with KEM ciphertext prepended

    Raises:
        EncryptionOptionError: If encryption_option is not supported
    """
    # Extract KEM public key from bundle
    kem_public = public_bundle[0 : config.kem_public_size]

    # Encapsulate to get shared secret
    with oqs.KeyEncapsulation(config.kem_algorithm) as kem:
        kem_ciphertext, shared_secret = kem.encap_secret(kem_public)

    # Encrypt data with shared secret using specified symmetric cipher
    if encryption_option == "AES-256-GCM":
        # Use first 32 bytes of shared secret as AES-256 key
        key = shared_secret[:32]
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        # Format: kem_ciphertext || nonce || ciphertext || tag
        return kem_ciphertext + cipher.nonce + ciphertext + tag

    elif encryption_option == "AES-128-GCM":
        # Use first 16 bytes of shared secret as AES-128 key
        key = shared_secret[:16]
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        return kem_ciphertext + cipher.nonce + ciphertext + tag

    elif encryption_option == "ChaCha20-Poly1305":
        # ChaCha20-Poly1305 implementation would go here
        # For now, we'll defer this to avoid adding another dependency
        # Would require: from Crypto.Cipher import ChaCha20_Poly1305
        try:
            from Crypto.Cipher import ChaCha20_Poly1305

            key = shared_secret[:32]
            cipher = ChaCha20_Poly1305.new(key=key)
            ciphertext, tag = cipher.encrypt_and_digest(data)
            return kem_ciphertext + cipher.nonce + ciphertext + tag
        except ImportError:
            raise EncryptionOptionError(
                f"{encryption_option} requires pycryptodome >= 3.7.0"
            )

    else:
        raise EncryptionOptionError(encryption_option)


def decrypt_hybrid(
    ciphertext: bytes,
    private_bundle: bytes,
    config: PQFamilyConfig,
    encryption_option: str = "AES-256-GCM",
) -> bytes:
    """Decrypt data using hybrid KEM/DEM decryption.

    The process:
    1. Extract KEM private key from bundle
    2. Parse ciphertext to extract KEM ciphertext, nonce, data, tag
    3. Use KEM to decapsulate and recover shared secret
    4. Decrypt data with shared secret using symmetric cipher

    Args:
        ciphertext: Encrypted data (kem_ciphertext || nonce || symmetric_ciphertext || tag)
        private_bundle: Bundled private key containing KEM private key
        config: Family configuration
        encryption_option: Symmetric cipher to use

    Returns:
        bytes: Decrypted plaintext data

    Raises:
        EncryptionOptionError: If encryption_option is not supported
        ValueError: If decryption fails (wrong key, corrupted data, etc.)
    """
    # Extract KEM private key from bundle
    kem_private = private_bundle[0 : config.kem_private_size]

    # Parse ciphertext components
    kem_ciphertext = ciphertext[0 : config.kem_ciphertext_size]

    # Decapsulate to recover shared secret
    with oqs.KeyEncapsulation(
        config.kem_algorithm, secret_key=kem_private
    ) as kem:
        shared_secret = kem.decap_secret(kem_ciphertext)

    # Decrypt data with shared secret
    if encryption_option == "AES-256-GCM":
        key = shared_secret[:32]
        nonce_start = config.kem_ciphertext_size
        nonce = ciphertext[nonce_start : nonce_start + 16]
        symmetric_ciphertext = ciphertext[nonce_start + 16 : -16]
        tag = ciphertext[-16:]

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(symmetric_ciphertext, tag)

    elif encryption_option == "AES-128-GCM":
        key = shared_secret[:16]
        nonce_start = config.kem_ciphertext_size
        nonce = ciphertext[nonce_start : nonce_start + 16]
        symmetric_ciphertext = ciphertext[nonce_start + 16 : -16]
        tag = ciphertext[-16:]

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(symmetric_ciphertext, tag)

    elif encryption_option == "ChaCha20-Poly1305":
        try:
            from Crypto.Cipher import ChaCha20_Poly1305

            key = shared_secret[:32]
            nonce_start = config.kem_ciphertext_size
            # ChaCha20 uses 12-byte nonce
            nonce = ciphertext[nonce_start : nonce_start + 12]
            symmetric_ciphertext = ciphertext[nonce_start + 12 : -16]
            tag = ciphertext[-16:]

            cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
            return cipher.decrypt_and_verify(symmetric_ciphertext, tag)
        except ImportError:
            raise EncryptionOptionError(
                f"{encryption_option} requires pycryptodome >= 3.7.0"
            )

    else:
        raise EncryptionOptionError(encryption_option)


def sign_data(
    data: bytes,
    private_bundle: bytes,
    config: PQFamilyConfig,
    signature_option: str = "direct",
) -> bytes:
    """Sign data using the signature private key from the bundle.

    Args:
        data: Data to sign
        private_bundle: Bundled private key containing signature private key
        config: Family configuration
        signature_option: Signature protocol ("direct", "prehash-SHA256", "prehash-SHA512")

    Returns:
        bytes: Digital signature

    Raises:
        SignatureOptionError: If signature_option is not supported
    """
    # Extract signature private key from bundle
    sig_private_start = config.kem_private_size
    sig_private = private_bundle[
        sig_private_start : sig_private_start + config.sig_private_size
    ]

    # Apply prehashing if requested
    data_to_sign = data
    if signature_option == "prehash-SHA256":
        data_to_sign = hashlib.sha256(data).digest()
    elif signature_option == "prehash-SHA512":
        data_to_sign = hashlib.sha512(data).digest()
    elif signature_option != "direct":
        raise SignatureOptionError(signature_option)

    # Sign the data
    with oqs.Signature(config.sig_algorithm, secret_key=sig_private) as signer:
        signature = signer.sign(data_to_sign)

    return signature


def verify_data_signature(
    signature: bytes,
    data: bytes,
    public_bundle: bytes,
    config: PQFamilyConfig,
    signature_option: str = "direct",
) -> bool:
    """Verify a signature using the signature public key from the bundle.

    Args:
        signature: Signature to verify
        data: Original data that was signed
        public_bundle: Bundled public key containing signature public key
        config: Family configuration
        signature_option: Signature protocol (must match signing option)

    Returns:
        bool: True if signature is valid, False otherwise

    Raises:
        SignatureOptionError: If signature_option is not supported
    """
    # Extract signature public key from bundle
    sig_public = public_bundle[config.kem_public_size :]

    # Apply prehashing if requested (must match signing)
    data_to_verify = data
    if signature_option == "prehash-SHA256":
        data_to_verify = hashlib.sha256(data).digest()
    elif signature_option == "prehash-SHA512":
        data_to_verify = hashlib.sha512(data).digest()
    elif signature_option != "direct":
        raise SignatureOptionError(signature_option)

    # Verify the signature
    with oqs.Signature(config.sig_algorithm) as verifier:
        return verifier.verify(data_to_verify, signature, sig_public)
