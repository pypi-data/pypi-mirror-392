"""Automated tests for crypt.Crypt's locking functionality"""

import _auto_run_with_pytest  # noqa

from datetime import datetime
from termcolor import colored as coloured


from multi_crypt import Crypt
from multi_crypt import verify_key_pair

from datetime import datetime
from termcolor import colored as coloured


from multi_crypt import Crypt, LockedError


PYTEST = False
BREAKPOINTS = False

CRYPTO_FAMILY = "EC-secp256k1"  # the cryptographic family to use for the tests


class SharedData:
    crypt: Crypt
    encryptor: Crypt


shared_data = SharedData()


def test_create_encryptor():
    crypt = Crypt.new(CRYPTO_FAMILY)

    start_time = datetime.utcnow()
    encryptor = Crypt(CRYPTO_FAMILY, public_key=crypt.public_key)
    duration = datetime.utcnow() - start_time

    assert encryptor.public_key == crypt.public_key, f"{
        crypt.family
    }: Created Crypt"
    shared_data.crypt = crypt
    shared_data.encryptor = encryptor


def test_encryption(encryption_options=None):
    crypt = shared_data.crypt
    encryptor = shared_data.encryptor

    original_data = b"Hello there!"

    start_time = datetime.utcnow()
    encrypted_data = encryptor.encrypt(original_data)
    duration = datetime.utcnow() - start_time

    encryption_success = (
        crypt.decrypt(encrypted_data, encryption_options=encryption_options)
        == original_data
    )
    assert encryption_success, f"{crypt.family}-{
        encryption_options
    }: Encryption"


def test_decryption_locking(encryption_options=None):
    crypt = shared_data.crypt
    encryptor = shared_data.encryptor

    original_data = b"Hello there!"
    encrypted_data = crypt.encrypt(original_data)

    locking: bool
    try:
        encryptor.decrypt(encrypted_data)
    except LockedError:
        # Crypt's decrypt successfully raised an exception
        locking = True
    else:
        # encryptor's decrypt didn't raise an error
        locking = False

    assert locking, f"{crypt.family}-{
        encryption_options
    }: Decryption locks correctly"


def test_signing_locking(signature_options=None):
    crypt = shared_data.crypt
    encryptor = shared_data.encryptor

    data = b"Hello there!"

    locking: bool
    try:
        encryptor.sign(data)
    except LockedError:
        # Crypt's decrypt successfully raised an exception
        locking = True
    else:
        # encryptor's decrypt didn't raise an error
        locking = False
    assert locking, f"{crypt.family}-{
        signature_options
    }: Signing locks correctly"


def test_verification(signature_options=None):
    crypt = shared_data.crypt
    encryptor = shared_data.encryptor

    data = b"Hello there!"

    signature = crypt.sign(data, signature_options=signature_options)

    start_time = datetime.utcnow()
    is_verified = encryptor.verify_signature(
        signature, data, signature_options=signature_options
    )
    duration = datetime.utcnow() - start_time

    assert is_verified, f"{crypt.family}-{
        signature_options
    }: Signature verification"


def test_unlocking(encryption_options=None, signature_options=None):
    crypt = shared_data.crypt
    encryptor = shared_data.encryptor
    encryptor.unlock(crypt.private_key)

    original_data = b"Hello there!"

    start_time = datetime.utcnow()
    encrypted_data = crypt.encrypt(original_data)
    decrypted_data = crypt.decrypt(encrypted_data)
    duration = datetime.utcnow() - start_time

    assert decrypted_data == original_data, f"{crypt.family}-{
        encryption_options
    }: Unlocked decryption"

    original_data = b"Hello there!"

    start_time = datetime.utcnow()
    signature = crypt.sign(original_data)
    is_verified = crypt.verify_signature(signature, original_data)
    duration = datetime.utcnow() - start_time

    assert is_verified, f"{crypt.family}-{signature_options}: Unlocked signing"


def run_tests():
    print("Running tests for Crypt locking:")

    test_create_encryptor(CRYPTO_FAMILY)
    test_encryption()
    test_decryption_locking()
    test_signing_locking()
    test_verification()
    test_unlocking()


if __name__ == "__main__":
    run_tests()
