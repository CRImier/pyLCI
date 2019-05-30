from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA512, SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util import Counter
from unpaddedbase64 import decode_base64, encode_base64

HEADER = '-----BEGIN MEGOLM SESSION DATA-----'
FOOTER = '-----END MEGOLM SESSION DATA-----'


def encrypt_and_save(data, outfile, passphrase, count=100000):
    """Encrypt keys data and write it to file.

    Args:
        data (bytes): The data to encrypt.
        outfile (str): The file the encrypted data will be written to.
        passphrase (str): The encryption passphrase.
        count (int): The round count used when deriving a key from the passphrase.

    Raises:
        FileNotFoundError if the path to the file did not exist.
    """
    encrypted_data = encrypt(data, passphrase, count=count)
    with open(outfile, 'w') as f:
        f.write(HEADER)
        f.write(encrypted_data)
        f.write(FOOTER)


def decrypt_and_read(infile, passphrase):
    """Decrypt keys data from file.

    Args:
        infile (str): The file the encrypted data will be written to.
        passphrase (str): The encryption passphrase.

    Returns:
        The decrypted data, as bytes.

    Raises:
        ValueError if something went wrong during decryption.
        FileNotFoundError if the file was not found.
    """
    with open(infile, 'r') as f:
        encrypted_data = f.read()
    encrypted_data = encrypted_data.replace('\n', '')

    if not encrypted_data.startswith(HEADER) or not encrypted_data.endswith(FOOTER):
        raise ValueError('Wrong file format.')

    encrypted_data = encrypted_data[len(HEADER):-len(FOOTER)]
    return decrypt(encrypted_data, passphrase)


def prf(passphrase, salt):
    """HMAC-SHA-512 pseudorandom function."""
    return HMAC.new(passphrase, salt, SHA512).digest()


def encrypt(data, passphrase, count=100000):
    # 128 bits salt
    salt = Random.new().read(16)
    # 512 bits derived key
    derived_key = PBKDF2(passphrase, salt, 64, count, prf)
    aes_key = derived_key[:32]
    hmac_key = derived_key[32:64]

    # 128 bits IV, which will be the initial value initial
    iv = int.from_bytes(Random.new().read(16), byteorder='big')
    # Set bit 63 to 0, as specified
    iv &= ~(1 << 63)
    ctr = Counter.new(128, initial_value=iv)
    cipher = AES.new(aes_key, AES.MODE_CTR, counter=ctr)
    encrypted_data = cipher.encrypt(data)

    payload = b''.join((
        bytes([1]),  # Version
        salt,
        int.to_bytes(iv, length=16, byteorder='big'),
        int.to_bytes(count, length=4, byteorder='big'),  # 32 bits big-endian round count
        encrypted_data
    ))

    hmac = HMAC.new(hmac_key, payload, SHA256).digest()
    return encode_base64(payload + hmac)


def decrypt(encrypted_payload, passphrase):
    encrypted_payload = decode_base64(encrypted_payload)

    version = encrypted_payload[0]
    if version != 1:
        raise ValueError('Unsupported export format version.')
    salt = encrypted_payload[1:17]
    iv = int.from_bytes(encrypted_payload[17:33], byteorder='big')
    count = int.from_bytes(encrypted_payload[33:37], byteorder='big')
    encrypted_data = encrypted_payload[37:-32]
    expected_hmac = encrypted_payload[-32:]

    derived_key = PBKDF2(passphrase, salt, 64, count, prf)
    aes_key = derived_key[:32]
    hmac_key = derived_key[32:64]

    hmac = HMAC.new(hmac_key, encrypted_payload[:-32], SHA256).digest()
    if hmac != expected_hmac:
        raise ValueError('HMAC check failed for encrypted payload.')

    ctr = Counter.new(128, initial_value=iv)
    cipher = AES.new(aes_key, AES.MODE_CTR, counter=ctr)
    return cipher.decrypt(encrypted_data)
