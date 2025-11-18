"""Automated tests for crypt.Crypt"""

import _auto_run_with_pytest  # noqa

from datetime import datetime
from termcolor import colored as coloured


from multi_crypt import Crypt
from multi_crypt import verify_key_pair


PYTEST = False
BREAKPOINTS = False

CRYPTO_FAMILY = "EC-secp256k1"  # the cryptographic family to use for the tests


class SharedData:
    crypt: Crypt


shared_data = SharedData()


def test_create_crypt():
    start_time = datetime.utcnow()
    crypt = Crypt.new(CRYPTO_FAMILY)

    reconstructed_crypt = Crypt(
        CRYPTO_FAMILY, crypt.private_key, crypt.public_key
    )
    duration = datetime.utcnow() - start_time

    key_sanity = verify_key_pair(
        CRYPTO_FAMILY, crypt.private_key, crypt.public_key
    )
    reconstruction_success = (
        crypt.private_key == reconstructed_crypt.private_key
        and crypt.public_key == reconstructed_crypt.public_key
    )

    shared_data.crypt = crypt
    assert key_sanity and reconstruction_success, f"{
        crypt.family
    }: Key Pair Check"


def test_encryption_decryption(encryption_options=None):
    crypt = shared_data.crypt
    original_data = b"Hello there!"

    start_time = datetime.utcnow()
    encrypted_data = crypt.encrypt(original_data)
    decrypted_data = crypt.decrypt(encrypted_data)
    duration = datetime.utcnow() - start_time

    assert decrypted_data == original_data, f"{crypt.family}-{
        encryption_options
    }: Encryption & Decryption"


def test_signing_verification(signature_options=None):
    crypt = shared_data.crypt
    original_data = b"Hello there!"

    start_time = datetime.utcnow()
    signature = crypt.sign(original_data)
    is_verified = crypt.verify_signature(signature, original_data)
    duration = datetime.utcnow() - start_time

    assert is_verified, f"{crypt.family}-{
        signature_options
    }: Signing & Verification"
