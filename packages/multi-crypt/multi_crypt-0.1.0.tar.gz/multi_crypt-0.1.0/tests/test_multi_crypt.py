import _auto_run_with_pytest  # noqa
import pytest
from datetime import datetime

import multi_crypt
from multi_crypt import (
    generate_keys,
    verify_key_pair,
    encrypt,
    decrypt,
    sign,
    verify_signature,
)

# ---------------------------------------------------------
# Build dynamic parameter lists at import time (pytest-safe)
# ---------------------------------------------------------

ALL_FAMILIES = multi_crypt.get_all_families()
ENCRYPTION_FAMILIES = multi_crypt.get_encryption_families()
SIGNATURE_FAMILIES = multi_crypt.get_signature_families()

# Build valid (family, option) combinations for encryption
ENCRYPTION_CASES = []
for fam in ENCRYPTION_FAMILIES:
    options = multi_crypt.get_encrytpion_options(fam)
    if not options:
        ENCRYPTION_CASES.append((fam, None))
    else:
        ENCRYPTION_CASES.append((fam, None))
        for opt in options:
            ENCRYPTION_CASES.append((fam, opt))

# Build valid (family, option) combinations for signatures
SIGNATURE_CASES = []
for fam in SIGNATURE_FAMILIES:
    options = multi_crypt.get_signature_options(fam)
    if not options:
        SIGNATURE_CASES.append((fam, None))
    else:
        SIGNATURE_CASES.append((fam, None))
        for opt in options:
            SIGNATURE_CASES.append((fam, opt))


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------


@pytest.mark.parametrize("family", ALL_FAMILIES)
def test_key_generation_check(family):
    public_key, private_key = generate_keys(family)
    assert verify_key_pair(family, private_key, public_key)


@pytest.mark.parametrize("family, encryption_options", ENCRYPTION_CASES)
def test_encryption_decryption(family, encryption_options):
    public_key, private_key = generate_keys(family)
    original_data = b"Hello there!"

    encrypted = encrypt(family, original_data, public_key, encryption_options)
    decrypted = decrypt(family, encrypted, private_key, encryption_options)

    assert decrypted == original_data


@pytest.mark.parametrize("family, signature_options", SIGNATURE_CASES)
def test_signing_verification(family, signature_options):
    public_key, private_key = generate_keys(family)

    data = b"Hello there!"
    alt_data = b"Hello, World!"

    signature = sign(family, data, private_key, signature_options)
    assert verify_signature(
        family, signature, data, public_key, signature_options
    )

    alt_signature = sign(family, alt_data, private_key, signature_options)
    assert not verify_signature(
        family, alt_signature, data, public_key, signature_options
    )
