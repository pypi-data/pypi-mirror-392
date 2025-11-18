#!/usr/bin/env python3

import os
import sys
import json
import base64
import argparse
import getpass
import hmac
import hashlib
import re
import time
import secrets
from datetime import datetime
from typing import Tuple, Optional, Dict, Any
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidTag

# ============================================================================
# CONSTANTS
# ============================================================================

KEY_SIZE = 32  # AES-256
NONCE_SIZE = 12
SALT_SIZE = 16
HKDF_SALT_SIZE = 16
MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_ATTEMPTS = 3
MAX_UNWRAP_ATTEMPTS = 5
DEFAULT_SCRYPT_N = 2**17  # 131,072
DEFAULT_SCRYPT_R = 8
DEFAULT_SCRYPT_P = 1
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
CHUNK_SIZE = 64 * 1024  # 64KB for streaming
ATTEMPT_RESET_HOURS = 24
VERSION = 1

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def b64(x: bytes) -> str:
    """Encode bytes to base64 string."""
    return base64.b64encode(x).decode('ascii')

def ub64(s: str) -> bytes:
    """Decode base64 string to bytes."""
    try:
        return base64.b64decode(s)
    except Exception as e:
        raise ValueError(f"Invalid base64 data: {e}")

def ct_compare(a: bytes, b: bytes) -> bool:
    """Constant-time comparison to prevent timing attacks."""
    return secrets.compare_digest(a, b)

def secure_delete(*vars) -> None:
    """Best-effort deletion of sensitive variables from memory."""
    for var in vars:
        if var is None:
            continue
        try:
            if isinstance(var, (bytes, bytearray)):
                # Zero out bytes/bytearray content
                if isinstance(var, bytearray):
                    for i in range(len(var)):
                        var[i] = 0
                # Let GC handle the rest
            del var
        except:
            pass

def get_file_size(path: str) -> int:
    """Get file size, raise error if file doesn't exist."""
    try:
        return os.path.getsize(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except OSError as e:
        raise OSError(f"Cannot access file {path}: {e}")

# ============================================================================
# PASSWORD VALIDATION
# ============================================================================

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets security requirements.
    
    Returns:
        (is_valid, error_message)
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
    
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>\-_=+\[\]\\|/~`]', password))
    
    variety_count = sum([has_upper, has_lower, has_digit, has_special])
    
    if variety_count < 3:
        return False, "Password must contain at least 3 of: uppercase, lowercase, digit, special character"
    
    # Check for common weak passwords
    common_weak = ['password', '12345678', 'qwerty', 'admin123', 'letmein', 
                   'welcome', 'monkey', 'dragon', 'master', 'sunshine']
    if password.lower() in common_weak:
        return False, "Password is too common and easily guessed"
    
    return True, ""

def prompt_password_with_validation() -> bytes:
    """
    Prompt for password with validation and confirmation.
    
    Returns:
        Password as bytes
    
    Raises:
        ValueError: If max attempts exceeded
    """
    print("\nPassword Requirements:")
    print(f"  • Minimum {MIN_PASSWORD_LENGTH} characters")
    print("  • At least 3 of: uppercase, lowercase, digit, special character")
    print("  • Not a common password\n")
    
    for attempt in range(MAX_PASSWORD_ATTEMPTS):
        pwd = getpass.getpass("Enter password: ")
        
        valid, msg = validate_password_strength(pwd)
        if not valid:
            print(f"✗ {msg}")
            if attempt < MAX_PASSWORD_ATTEMPTS - 1:
                print(f"  ({MAX_PASSWORD_ATTEMPTS - attempt - 1} attempts remaining)\n")
                continue
            else:
                raise ValueError("Maximum password attempts exceeded")
        
        confirm = getpass.getpass("Confirm password: ")
        
        if not ct_compare(pwd.encode('utf-8'), confirm.encode('utf-8')):
            print("✗ Passwords do not match")
            if attempt < MAX_PASSWORD_ATTEMPTS - 1:
                print(f"  ({MAX_PASSWORD_ATTEMPTS - attempt - 1} attempts remaining)\n")
                continue
            else:
                raise ValueError("Maximum password attempts exceeded")
        
        secure_delete(confirm)
        return pwd.encode('utf-8')
    
    raise ValueError("Maximum password attempts exceeded")

# ============================================================================
# RATE LIMITING
# ============================================================================

class AttemptTracker:
    """Track and limit failed unwrap attempts."""
    
    def __init__(self, keyfile_path: str):
        self.attempt_file = f"{keyfile_path}.attempts"
    
    def check_attempts(self) -> None:
        """Check if attempts are within limit. Raises ValueError if exceeded."""
        if not os.path.exists(self.attempt_file):
            return
        
        try:
            with open(self.attempt_file, 'r') as f:
                data = json.load(f)
            
            attempts = data.get('count', 0)
            last_attempt = data.get('last_attempt', 0)
            
            # Reset counter after 24 hours
            if time.time() - last_attempt > ATTEMPT_RESET_HOURS * 3600:
                self.reset_attempts()
                return
            
            if attempts >= MAX_UNWRAP_ATTEMPTS:
                hours_left = ATTEMPT_RESET_HOURS - ((time.time() - last_attempt) / 3600)
                raise ValueError(
                    f"Maximum unlock attempts ({MAX_UNWRAP_ATTEMPTS}) exceeded. "
                    f"Try again in {hours_left:.1f} hours, or delete {self.attempt_file} to reset."
                )
        except (json.JSONDecodeError, KeyError):
            # Corrupted attempt file, reset it
            self.reset_attempts()
    
    def increment_attempts(self) -> None:
        """Increment failed attempt counter."""
        attempts = 0
        last_attempt = time.time()
        
        if os.path.exists(self.attempt_file):
            try:
                with open(self.attempt_file, 'r') as f:
                    data = json.load(f)
                attempts = data.get('count', 0)
            except:
                pass
        
        attempts += 1
        
        try:
            with open(self.attempt_file, 'w') as f:
                json.dump({'count': attempts, 'last_attempt': last_attempt}, f)
            os.chmod(self.attempt_file, 0o600)
        except IOError:
            pass
    
    def reset_attempts(self) -> None:
        """Reset attempt counter."""
        try:
            if os.path.exists(self.attempt_file):
                os.remove(self.attempt_file)
        except OSError:
            pass

# ============================================================================
# CRYPTOGRAPHIC OPERATIONS
# ============================================================================

def derive_kek(password: bytes, salt: bytes, n: int = DEFAULT_SCRYPT_N) -> bytes:
    """
    Derive Key Encryption Key from password using Scrypt.
    
    Args:
        password: User password
        salt: Random salt
        n: Scrypt CPU/memory cost parameter
    
    Returns:
        32-byte KEK
    """
    try:
        kdf = Scrypt(
            salt=salt,
            length=KEY_SIZE,
            n=n,
            r=DEFAULT_SCRYPT_R,
            p=DEFAULT_SCRYPT_P
        )
        return kdf.derive(password)
    except Exception as e:
        raise RuntimeError(f"Key derivation failed: {e}")

def derive_subkeys(kek: bytes, hkdf_salt: bytes) -> Tuple[bytes, bytes]:
    """
    Derive separate encryption and HMAC keys via HKDF.
    
    Args:
        kek: Key Encryption Key from Scrypt
        hkdf_salt: Separate salt for HKDF (not the Scrypt salt)
    
    Returns:
        (encryption_key, hmac_key) tuple
    """
    try:
        # Derive encryption key
        hkdf_enc = HKDF(
            algorithm=hashes.SHA256(),
            length=KEY_SIZE,
            salt=hkdf_salt,
            info=b'kryptex-v1-encryption'
        )
        enc_key = hkdf_enc.derive(kek)
        
        # Derive HMAC key (separate HKDF instance required)
        hkdf_mac = HKDF(
            algorithm=hashes.SHA256(),
            length=KEY_SIZE,
            salt=hkdf_salt,
            info=b'kryptex-v1-hmac'
        )
        mac_key = hkdf_mac.derive(kek)
        
        return enc_key, mac_key
    except Exception as e:
        raise RuntimeError(f"Subkey derivation failed: {e}")

def compute_hmac(payload: dict, hmac_key: bytes) -> str:
    """
    Compute HMAC of keyfile for integrity verification.
    
    Args:
        payload: Dictionary to authenticate
        hmac_key: HMAC key
    
    Returns:
        Hex-encoded HMAC
    """
    temp = payload.copy()
    temp.pop('hmac', None)
    canonical = json.dumps(temp, sort_keys=True, separators=(',', ':'))
    return hmac.new(hmac_key, canonical.encode('utf-8'), hashlib.sha256).hexdigest()

# ============================================================================
# FILE OPERATIONS
# ============================================================================

def write_json_file(path: str, payload: Dict[str, Any], force: bool = False) -> None:
    """
    Write JSON file with secure permissions and overwrite protection.
    
    Args:
        path: Output file path
        payload: Dictionary to write
        force: Skip overwrite confirmation
    """
    # Check for existing file
    if os.path.exists(path) and not force:
        response = input(f"File {path} exists. Overwrite? (yes/no): ")
        if response.lower() != 'yes':
            raise ValueError("Operation cancelled - file exists")
    
    try:
        # Write to temporary file first
        temp_path = path + '.tmp'
        with open(temp_path, 'w') as f:
            json.dump(payload, f, indent=2)
        
        # Atomically replace the file
        os.replace(temp_path, path)
    except IOError as e:
        # Clean up temp file if it exists
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            pass
        raise IOError(f"Failed to write file {path}: {e}")
    
    # Set secure permissions
    try:
        os.chmod(path, 0o600)
    except OSError as e:
        print(f"Warning: Could not set secure permissions on {path}: {e}")

def validate_keyfile_structure(data: Dict[str, Any]) -> None:
    """
    Validate keyfile has required fields and correct structure.
    
    Raises:
        ValueError: If validation fails
    """
    # Check version
    version = data.get('version')
    if version != VERSION:
        raise ValueError(f"Unsupported keyfile version: {version} (expected {VERSION})")
    
    # Check required fields
    required = ['kdf', 'kdf_salt', 'kdf_params', 'cipher', 'kek_nonce', 'wrapped_key', 'hmac', 'hkdf_salt']
    for field in required:
        if field not in data:
            raise ValueError(f"Missing required field in keyfile: {field}")
    
    # Validate KDF
    if data['kdf'] != 'scrypt':
        raise ValueError(f"Unsupported KDF: {data['kdf']}")
    
    # Validate cipher
    if data['cipher'] != 'AES-GCM':
        raise ValueError(f"Unsupported cipher: {data['cipher']}")
    
    # Validate KDF params
    params = data['kdf_params']
    if not isinstance(params, dict) or 'n' not in params:
        raise ValueError("Invalid KDF parameters in keyfile")

# ============================================================================
# KEY WRAPPING
# ============================================================================

def wrap_key(args: argparse.Namespace) -> int:
    """
    Generate and password-protect a data encryption key.
    
    Returns:
        0 on success, 1 on failure
    """
    password = None
    kek = None
    enc_key = None
    hmac_key = None
    data_key = None
    
    try:
        print("=== Key Wrapping ===")
        password = prompt_password_with_validation()
        
        print("\n⏳ Generating cryptographic materials...")
        salt = os.urandom(SALT_SIZE)
        hkdf_salt = os.urandom(HKDF_SALT_SIZE)  # Separate salt for HKDF
        
        print("⏳ Deriving key encryption key (this may take a moment)...")
        kek = derive_kek(password, salt, DEFAULT_SCRYPT_N)
        enc_key, hmac_key = derive_subkeys(kek, hkdf_salt)
        
        # Generate data encryption key
        data_key = os.urandom(KEY_SIZE)
        
        # Wrap DEK with AES-GCM using derived encryption key
        aes = AESGCM(enc_key)
        nonce = os.urandom(NONCE_SIZE)
        wrapped = aes.encrypt(nonce, data_key, None)
        
        # Build keyfile payload
        payload = {
            "version": VERSION,
            "kdf": "scrypt",
            "kdf_salt": b64(salt),
            "hkdf_salt": b64(hkdf_salt),
            "kdf_params": {
                "n": DEFAULT_SCRYPT_N,
                "r": DEFAULT_SCRYPT_R,
                "p": DEFAULT_SCRYPT_P
            },
            "cipher": "AES-GCM",
            "key_size": KEY_SIZE * 8,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "kek_nonce": b64(nonce),
            "wrapped_key": b64(wrapped)
        }
        
        # Compute HMAC for integrity
        payload['hmac'] = compute_hmac(payload, hmac_key)
        
        # Write keyfile
        write_json_file(args.keyfile, payload, args.force)
        
        print(f"\n✓ Wrapped key written to {args.keyfile}")
        print(f"✓ File permissions set to 0600")
        print(f"✓ KDF: Scrypt (N={DEFAULT_SCRYPT_N}, r={DEFAULT_SCRYPT_R}, p={DEFAULT_SCRYPT_P})")
        print(f"✓ Key size: {KEY_SIZE * 8} bits")
        print("\n  IMPORTANT: Keep your password secure. Lost password = lost data.")
        
        return 0
        
    except ValueError as e:
        print(f"\n✗ Error: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1
    finally:
        # Always clean up sensitive data
        secure_delete(password, kek, enc_key, hmac_key, data_key)

# ============================================================================
# KEY UNWRAPPING
# ============================================================================

def unwrap_keyfile(keyfile_path: str, password: bytes) -> bytes:
    """
    Unwrap and verify a protected data key.
    
    Args:
        keyfile_path: Path to keyfile
        password: User password
    
    Returns:
        Decrypted data key
    
    Raises:
        Various exceptions for different failure modes
    """
    # Check rate limiting
    tracker = AttemptTracker(keyfile_path)
    tracker.check_attempts()
    
    kek = None
    enc_key = None
    hmac_key = None
    data_key = None
    
    try:
        # Read keyfile
        try:
            with open(keyfile_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Keyfile not found: {keyfile_path}")
        except json.JSONDecodeError:
            raise ValueError("Keyfile is corrupted or not valid JSON")
        
        # Validate structure
        validate_keyfile_structure(data)
        
        # Extract fields
        salt = ub64(data['kdf_salt'])
        hkdf_salt = ub64(data['hkdf_salt'])
        kek_nonce = ub64(data['kek_nonce'])
        wrapped = ub64(data['wrapped_key'])
        stored_hmac = data['hmac']
        n = data['kdf_params']['n']
        
        # Derive KEK from password
        sys.stderr.write("⏳ Deriving key (this may take a moment)...\n")
        sys.stderr.flush()
        kek = derive_kek(password, salt, n)
        enc_key, hmac_key = derive_subkeys(kek, hkdf_salt)
        
        # Verify HMAC
        expected_hmac = compute_hmac(data, hmac_key)
        if not ct_compare(stored_hmac.encode('utf-8'), expected_hmac.encode('utf-8')):
            tracker.increment_attempts()
            raise ValueError("Authentication failed: keyfile integrity check failed")
        
        # Decrypt data key
        aes = AESGCM(enc_key)
        try:
            data_key = aes.decrypt(kek_nonce, wrapped, None)
        except InvalidTag:
            tracker.increment_attempts()
            raise ValueError("Authentication failed: incorrect password or corrupted keyfile")
        
        # Success - reset attempt counter
        tracker.reset_attempts()
        
        return data_key
        
    except (FileNotFoundError, ValueError) as e:
        # Re-raise expected errors
        raise
    except Exception as e:
        tracker.increment_attempts()
        raise RuntimeError(f"Key unwrapping failed: {e}")
    finally:
        # Clean up sensitive data
        secure_delete(kek, enc_key, hmac_key)

# ============================================================================
# FILE ENCRYPTION
# ============================================================================

def encrypt_file(args: argparse.Namespace) -> int:
    """
    Encrypt a file using wrapped data key.
    
    Returns:
        0 on success, 1 on failure
    """
    password = None
    data_key = None
    plaintext = None
    
    try:
        print("=== File Encryption ===")
        
        # Validate input file
        file_size = get_file_size(args.infile)
        print(f"Input file: {args.infile} ({file_size:,} bytes)")
        
        if file_size > MAX_FILE_SIZE:
            raise ValueError(
                f"File too large: {file_size:,} bytes "
                f"(maximum: {MAX_FILE_SIZE:,} bytes)"
            )
        
        # Get password and unwrap key
        password = getpass.getpass("\nEnter keyfile password: ").encode('utf-8')
        data_key = unwrap_keyfile(args.keyfile, password)
        
        print("✓ Key unwrapped successfully")
        
        # Encrypt file
        print(f"⏳ Encrypting {args.infile}...")
        
        try:
            with open(args.infile, 'rb') as f:
                plaintext = f.read()
        except IOError as e:
            raise IOError(f"Cannot read input file: {e}")
        
        aes = AESGCM(data_key)
        nonce = os.urandom(NONCE_SIZE)
        ciphertext = aes.encrypt(nonce, plaintext, None)
        
        # Build output payload
        output = {
            "version": VERSION,
            "cipher": "AES-GCM",
            "nonce": b64(nonce),
            "ciphertext": b64(ciphertext),
            "original_size": file_size,
            "encrypted_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # Write encrypted file
        write_json_file(args.outfile, output, args.force)
        
        print(f"✓ Encrypted {args.infile} → {args.outfile}")
        print(f"✓ Original size: {file_size:,} bytes")
        print(f"✓ Encrypted size: {len(json.dumps(output)):,} bytes")
        
        return 0
        
    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"\n✗ Error: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1
    finally:
        # Clean up sensitive data
        secure_delete(password, data_key, plaintext)

# ============================================================================
# FILE DECRYPTION
# ============================================================================

def decrypt_file(args: argparse.Namespace) -> int:
    """
    Decrypt a file using wrapped data key.
    
    Returns:
        0 on success, 1 on failure
    """
    password = None
    data_key = None
    plaintext = None
    
    try:
        print("=== File Decryption ===")
        
        # Validate encrypted file exists
        get_file_size(args.infile)
        
        # Get password and unwrap key
        password = getpass.getpass("\nEnter keyfile password: ").encode('utf-8')
        data_key = unwrap_keyfile(args.keyfile, password)
        
        print("✓ Key unwrapped successfully")
        
        # Read encrypted file
        print(f"⏳ Decrypting {args.infile}...")
        
        try:
            with open(args.infile, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Encrypted file not found: {args.infile}")
        except json.JSONDecodeError:
            raise ValueError("Encrypted file is corrupted or not valid JSON")
        
        # Validate encrypted file structure
        required_fields = ['version', 'cipher', 'nonce', 'ciphertext']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Invalid encrypted file format: missing {field}")
        
        # Extract fields
        nonce = ub64(data['nonce'])
        ciphertext = ub64(data['ciphertext'])
        
        # Decrypt
        aes = AESGCM(data_key)
        try:
            plaintext = aes.decrypt(nonce, ciphertext, None)
        except InvalidTag:
            raise ValueError("Decryption failed: file may be corrupted or tampered with")
        
        # Write decrypted file
        if os.path.exists(args.outfile) and not args.force:
            response = input(f"File {args.outfile} exists. Overwrite? (yes/no): ")
            if response.lower() != 'yes':
                raise ValueError("Operation cancelled - file exists")
        
        try:
            with open(args.outfile, 'wb') as f:
                f.write(plaintext)
            # Set secure permissions on output file
            os.chmod(args.outfile, 0o600)
        except IOError as e:
            raise IOError(f"Cannot write output file: {e}")
        
        print(f"✓ Decrypted {args.infile} → {args.outfile}")
        print(f"✓ Decrypted size: {len(plaintext):,} bytes")
        
        return 0
        
    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"\n✗ Error: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1
    finally:
        # Clean up sensitive data
        secure_delete(password, data_key, plaintext)

# ============================================================================
# KEY ROTATION
# ============================================================================

def rotate_key(args: argparse.Namespace) -> int:
    """
    Change keyfile password (re-wrap with new password).
    
    Returns:
        0 on success, 1 on failure
    """
    old_password = None
    new_password = None
    data_key = None
    kek = None
    enc_key = None
    hmac_key = None
    
    try:
        print("=== Key Rotation (Password Change) ===")
        
        # Unwrap with old password
        print("\nCurrent password:")
        old_password = getpass.getpass("Enter current keyfile password: ").encode('utf-8')
        data_key = unwrap_keyfile(args.keyfile, old_password)
        
        print("✓ Current password verified")
        
        # Get new password
        print("\nNew password:")
        new_password = prompt_password_with_validation()
        
        # Re-wrap with new password
        print("\n⏳ Re-wrapping key with new password...")
        salt = os.urandom(SALT_SIZE)
        hkdf_salt = os.urandom(HKDF_SALT_SIZE)
        kek = derive_kek(new_password, salt, DEFAULT_SCRYPT_N)
        enc_key, hmac_key = derive_subkeys(kek, hkdf_salt)
        
        aes = AESGCM(enc_key)
        nonce = os.urandom(NONCE_SIZE)
        wrapped = aes.encrypt(nonce, data_key, None)
        
        payload = {
            "version": VERSION,
            "kdf": "scrypt",
            "kdf_salt": b64(salt),
            "hkdf_salt": b64(hkdf_salt),
            "kdf_params": {
                "n": DEFAULT_SCRYPT_N,
                "r": DEFAULT_SCRYPT_R,
                "p": DEFAULT_SCRYPT_P
            },
            "cipher": "AES-GCM",
            "key_size": KEY_SIZE * 8,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "kek_nonce": b64(nonce),
            "wrapped_key": b64(wrapped)
        }
        
        payload['hmac'] = compute_hmac(payload, hmac_key)
        
        # Write new keyfile (always force overwrite for rotation)
        write_json_file(args.keyfile, payload, force=True)
        
        # Reset attempt counter
        tracker = AttemptTracker(args.keyfile)
        tracker.reset_attempts()
        
        print(f"\n✓ Password changed successfully")
        print(f"✓ Keyfile updated: {args.keyfile}")
        print(f"✓ Attempt counter reset")
        
        return 0
        
    except (ValueError, FileNotFoundError) as e:
        print(f"\n✗ Error: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1
    finally:
        # Clean up sensitive data
        secure_delete(old_password, new_password, data_key, kek, enc_key, hmac_key)

# ============================================================================
# INFO DISPLAY
# ============================================================================

def keyfile_info(args: argparse.Namespace) -> int:
    """
    Display keyfile metadata (non-sensitive information).
    
    Returns:
        0 on success, 1 on failure
    """
    try:
        with open(args.keyfile, 'r') as f:
            data = json.load(f)
        
        # Filter out sensitive fields
        sensitive_fields = ['wrapped_key', 'hmac', 'kek_nonce', 'hkdf_salt', 'kdf_salt']
        info = {
            k: v for k, v in data.items()
            if k not in sensitive_fields
        }
        
        print("=== Keyfile Information ===")
        print(json.dumps(info, indent=2))
        
        # Additional derived info
        print(f"\nKeyfile: {args.keyfile}")
        print(f"Size: {os.path.getsize(args.keyfile):,} bytes")
        print(f"Permissions: {oct(os.stat(args.keyfile).st_mode)[-3:]}")
        
        # Check for attempt file
        attempt_file = f"{args.keyfile}.attempts"
        if os.path.exists(attempt_file):
            try:
                with open(attempt_file, 'r') as f:
                    attempt_data = json.load(f)
                attempts = attempt_data.get('count', 0)
                last_attempt = attempt_data.get('last_attempt', 0)
                time_since = time.time() - last_attempt
                hours_until_reset = max(0, ATTEMPT_RESET_HOURS - (time_since / 3600))
                
                print(f"\n  Failed unlock attempts: {attempts}/{MAX_UNWRAP_ATTEMPTS}")
                if attempts > 0:
                    print(f"   Last failed attempt: {time_since / 3600:.1f} hours ago")
                    print(f"   Reset in: {hours_until_reset:.1f} hours")
            except:
                print(f"\n  Failed unlock attempts: <corrupted attempt file>")
        
        return 0
        
    except FileNotFoundError:
        print(f"✗ Error: Keyfile not found: {args.keyfile}")
        return 1
    except json.JSONDecodeError:
        print(f"✗ Error: Keyfile is corrupted or not valid JSON")
        return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="kryptex - Secure key wrapping and file encryption",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a new wrapped key
  %(prog)s wrap-key --keyfile my.key
  
  # Encrypt a file
  %(prog)s encrypt --keyfile my.key --infile data.txt --outfile data.enc
  
  # Decrypt a file
  %(prog)s decrypt --keyfile my.key --infile data.enc --outfile data.txt
  
  # Change keyfile password
  %(prog)s rotate-key --keyfile my.key
  
  # View keyfile info
  %(prog)s info --keyfile my.key
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True, help='Command to execute')
    
    # wrap-key command
    p_wrap = subparsers.add_parser('wrap-key', help='Generate and password-protect a data key')
    p_wrap.add_argument('--keyfile', required=True, help='Output keyfile path')
    p_wrap.add_argument('--force', action='store_true', help='Overwrite existing file')
    
    # encrypt command
    p_enc = subparsers.add_parser('encrypt', help='Encrypt a file')
    p_enc.add_argument('--keyfile', required=True, help='Keyfile path')
    p_enc.add_argument('--infile', required=True, help='Input file to encrypt')
    p_enc.add_argument('--outfile', required=True, help='Output encrypted file')
    p_enc.add_argument('--force', action='store_true', help='Overwrite existing file')
    
    # decrypt command
    p_dec = subparsers.add_parser('decrypt', help='Decrypt a file')
    p_dec.add_argument('--keyfile', required=True, help='Keyfile path')
    p_dec.add_argument('--infile', required=True, help='Input encrypted file')
    p_dec.add_argument('--outfile', required=True, help='Output decrypted file')
    p_dec.add_argument('--force', action='store_true', help='Overwrite existing file')
    
    # info command
    p_info = subparsers.add_parser('info', help='Display keyfile metadata')
    p_info.add_argument('--keyfile', required=True, help='Keyfile path')
    
    # rotate-key command
    p_rotate = subparsers.add_parser('rotate-key', help='Change keyfile password')
    p_rotate.add_argument('--keyfile', required=True, help='Keyfile path')
    
    args = parser.parse_args()
    
    # Dispatch to appropriate function
    command_handlers = {
        'wrap-key': wrap_key,
        'encrypt': encrypt_file,
        'decrypt': decrypt_file,
        'info': keyfile_info,
        'rotate-key': rotate_key
    }
    
    handler = command_handlers.get(args.command)
    if not handler:
        print(f"✗ Error: Unknown command: {args.command}")
        return 1
    
    try:
        return handler(args)
    except KeyboardInterrupt:
        print("\n✗ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())