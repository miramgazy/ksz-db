import base64
import logging
from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

def _get_fernet():
    key = getattr(settings, 'FERNET_SECRET_KEY', None)
    if not key:
        # Fallback key for dev if not configured
        key = b'XUZtgJj3iTRXLjYDM2S3tSIdBTmf5hsqHR0FkaxsJJo='
    if isinstance(key, str):
        key = key.encode('utf-8')
    return Fernet(key)

def encrypt_password(plain_text: str) -> str:
    """
    Encrypts plain text password using Fernet (AES-128 in CBC mode with SHA256 HMAC).
    Returns token as ASCII string prefixed with 'enc:'.
    """
    if not plain_text:
        return ''
    try:
        f = _get_fernet()
        token = f.encrypt(plain_text.encode('utf-8'))
        return 'enc:' + token.decode('ascii')
    except Exception as e:
        logger.error(f"Error encrypting password: {e}")
        return plain_text

def decrypt_password(cipher_text: str) -> str:
    """
    Decrypts encrypted password string.
    Supports:
      1. 'enc:...' -> Fernet encrypted token.
      2. Legacy Base64 string -> decodes Base64.
      3. Plain text fallback.
    """
    if not cipher_text:
        return ''

    # Check for Fernet encrypted token
    if cipher_text.startswith('enc:'):
        raw_token = cipher_text[4:].encode('ascii')
        try:
            f = _get_fernet()
            return f.decrypt(raw_token).decode('utf-8')
        except (InvalidToken, Exception) as e:
            logger.warning(f"Failed to decrypt Fernet token: {e}")
            return cipher_text

    # Check for legacy Base64 string from MS Access (e.g. 'cmVzdG9AdA==' or 'Q1E1NlI0NTI=')
    # If valid base64 and decodes into printable utf-8, return decoded
    try:
        decoded_bytes = base64.b64decode(cipher_text.encode('ascii'), validate=True)
        decoded_str = decoded_bytes.decode('utf-8')
        # Check if re-encoding matches (proper base64)
        if base64.b64encode(decoded_bytes).decode('ascii') == cipher_text.strip():
            return decoded_str
    except Exception:
        pass

    # Return as plain text
    return cipher_text
