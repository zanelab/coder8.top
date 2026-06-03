---
layout: post
title: "How Bitwarden Encrypts and Decrypts Your Passwords"
subtitle: ""
banner:
  image: /assets/images/posts/2026-06-03-how-bitwarden-encrypts-and-decrypts-your-passwords.jpg
  opacity: 0.7
author: zane.deng
categories: [Security, Cryptography]
tags:
- Password Manager
- Bitwarden
- Encryption
- Python
---

> *Deep dive into password manager cryptography: PBKDF2 → HKDF → AES-256-CBC → HMAC-SHA256, with complete runnable Python code.*

---

## Why You Should Care About Bitwarden's Cryptographic Design

To reduce my dependence on big tech, I've been researching how to self-host my password manager. One promising option is Vaultwarden—an open-source clone of the Bitwarden cloud server. This server has an interesting feature: all passwords are stored in a standard SQLite database, so besides having a self-hosted password server, I can also keep database backups locally for direct querying. Of course, these passwords are encrypted in that database, so figuring out how to decrypt them is essential—much like what Bitwarden clients do.

Speaking of Bitwarden clients, I happened to be writing this article when the official Bitwarden CLI client was compromised in a supply chain attack. This tool is what I personally use, installed on every computer I own—so this was a wake-up call. Fortunately, I didn't have the compromised version installed, but I think this precisely illustrates the value of building your own password management client rather than relying on the mainstream tool that all hackers are targeting!

In this article, I'll share how password encryption works in Bitwarden and its Vaultwarden clone, with complete runnable Python code.

---

## The Encryption Architecture: A Complete Overview

Bitwarden, Vaultwarden, and virtually every half-decent password manager encrypt all your passwords before storing them on the server. "Password" doesn't just mean the password itself—it also includes usernames, URLs, notes, attachments, and all other information you store for each entry. Bitwarden even encrypts the name of each password entry. Only the client knows how to encrypt or decrypt, and it always encrypts data before sending it to the server. The server only knows how to store and retrieve encrypted data blocks.

**Core Design Principle**: The server never sees your plaintext passwords.

### The Two-Layer Key Architecture

To encrypt and decrypt passwords, the client uses a master key associated with your account.

```
Account Passphrase
        ↓ PBKDF2 (600,000 iterations)
        ↓
    temp_key (32 bytes)
        ↓ HKDF-Expand (split into enc + mac)
        ↓
┌─────────────────┬─────────────────┐
│   enc_key (32B) │   mac_key (32B) │
│   AES encryption │   MAC signature │
└─────────────────┴─────────────────┘
```

Your account passphrase doesn't directly encrypt your passwords—it only encrypts the master key. To decrypt your passwords, the Bitwarden client:

1. First decrypts the master key using your passphrase
2. Then decrypts your actual passwords using the master key

When the client keeps your vault unlocked, it simply means it's retaining a decrypted copy of the master key in memory (or the entire decrypted vault), so it can continue serving your passwords without you re-entering your passphrase. To lock the vault, the client simply discards the master key.

---

## The Master Key: 64 Bytes of Randomness

The master key is a 64-byte random sequence generated on the client when you create your account. Generating a master key in Python is trivial:

```python
import os
master_key = os.urandom(64)  # 64 bytes = 512 bits
```

Bitwarden splits this key into two halves of 32 bytes each:

```python
# FOR DEMONSTRATION PURPOSES ONLY - never use in production
master_key = b'\xa3?\xbc\x86\x18\x7f\x9c|\xe2\xf1\x10\xd4\xee B\xde\x93\x12g\x03\\\x83\x9a\xc5S'
enc_key = master_key[:32]   # First 32 bytes: 256-bit encryption key
mac_key = master_key[32:]   # Last 32 bytes: message authentication key
```

---

## Decrypting a Password: The Full Process

First, here's what a password looks like stored in the Bitwarden database:

```python
encrypted_secret = '2.IkWFb104bXv7Zwl7eFbsnQ==|SB42jIOvjhV32hSusW/J7WfAnQV8DKIV/CJQB7IDaiz4lQv4lIcXzWp9+IT0ncVQ|S8Tcp2klhcOOzZvoA0C9WRURaWUq+U1F9jbuBskDIz0='
```

The encryption format: `version.IV|CipherText|MAC`

### Step 1: Parse the Encrypted String

```python
from base64 import b64decode

version, payload = encrypted_secret.split('.', 2)
if version != '2':
    raise ValueError('Unsupported encryption version')

fields = payload.split('|')
if len(fields) != 3:
    raise ValueError('Invalid encrypted data')

iv = b64decode(fields[0])
ciphertext = b64decode(fields[1])
mac = b64decode(fields[2])
```

### Step 2: MAC Verification (Integrity Check)

Before attempting to decrypt, you must ensure the encrypted string hasn't been corrupted or tampered with:

```python
import hmac, hashlib

calculated_mac = hmac.new(mac_key, iv + ciphertext, hashlib.sha256).digest()
if not hmac.compare_digest(calculated_mac, mac):
    raise ValueError('Invalid data or key')
```

**Important**: HMAC uses SHA-256 with the mac_key portion of the master key. If they don't match, the encrypted string has been corrupted or tampered with and should be discarded.

### Step 3: AES-256-CBC Decryption

Bitwarden uses AES (Advanced Encryption Standard) with specific parameters:
- **Algorithm**: AES-256-CBC
- **Block size**: 128 bits
- **Padding**: PKCS#7
- **IV**: Obtained from the iv portion of the encrypted string

```python
import pyaes  # requires: pip install pyaes

decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(enc_key, iv))
secret = decrypter.feed(ciphertext) + decrypter.feed()
print(secret)  # b'The quick brown fox jumps over the lazy dog'
```

---

## Complete Decryption Script

Here's the complete script for decrypting Bitwarden passwords:

```python
import os, hmac, hashlib, pyaes
from base64 import b64decode

# Master key (demo only - never use real keys in code)
master_key = b'\xa3?\xbc\x86\x18\x7f\x9c|\xe2\xf1\x10\xd4\xee B\xde\x93\x12g\x03\\\x83\x9a\xc5S'
enc_key = master_key[:32]
mac_key = master_key[32:]

# Encrypted password from database
encrypted_secret = '2.IkWFb104bXv7Zwl7eFbsnQ==|SB42jIOvjhV32hSusW/J7WfAnQV8DKIV/CJQB7IDaiz4lQv4lIcXzWp9+IT0ncVQ|S8Tcp2klhcOOzZvoA0C9WRURaWUq+U1F9jbuBskDIz0='

# Parse
version, payload = encrypted_secret.split('.', 2)
fields = payload.split('|')
iv = b64decode(fields[0])
ciphertext = b64decode(fields[1])
mac = b64decode(fields[2])

# Verify MAC
calculated_mac = hmac.new(mac_key, iv + ciphertext, hashlib.sha256).digest()
if not hmac.compare_digest(calculated_mac, mac):
    raise ValueError('Invalid data or key')

# Decrypt
decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(enc_key, iv))
secret = decrypter.feed(ciphertext) + decrypter.feed()
print(f'Decrypted: {secret.decode()}')
# Output: The quick brown fox jumps over the lazy dog
```

---

## Decrypting the Master Key: From Passphrase to Working Keys

In the example above, the master key was hardcoded. In reality, the master key itself is stored encrypted—you need to input your email and passphrase to decrypt it.

### Encrypted Master Key Format

```python
encrypted_master_key = '2.i5dH92a79wJ8L8tsqQEdLw==|a5swb8CeW5cTM2N+XQZCF+mX263BMaag+ghxiu+ci4W+fqqLZ82g+i7ReIcdiPLafoCAmeWZE48PETGJOsoOb6DcrK3sRdvHCx8xbRt1Xas='
```

Decrypting the master key uses the exact same algorithm as decrypting passwords—the difference is that enc_key and mac_key are derived from the user's email and passphrase.

### Key Derivation: PBKDF2 + HKDF

```python
from getpass import getpass

email = input('Email address: ')
passphrase = getpass('Passphrase: ')

# Step 1: PBKDF2 key derivation
# 600,000 iterations to increase brute-force cost
temp_key = hashlib.pbkdf2_hmac(
    'sha256',
    passphrase.encode(),
    email.encode(),
    600000,  # iteration count (Bitwarden default)
    32       # output length (32 bytes)
)
```

**Why 600,000 iterations?** This makes brute-force attacks extraordinarily expensive. If hackers try to crack your password with a dictionary attack, each guess requires 600,000 SHA-256 calculations—this dramatically improves security.

### HKDF Key Stretching

Generate two independent keys (enc_key and mac_key) from temp_key:

```python
def hkdf_expand(key, info, length, hash_func):
    """HKDF-Expand: derive multiple sub-keys from one source key"""
    prk = hmac.new(key, b'bits', hash_func).digest()
    t = b''
    result = b''
    counter = 1
    while len(result) < length:
        t = hmac.new(key, t + info + bytes([counter]), hash_func).digest()
        result += t
        counter += 1
    return result[:length]

# Generate encryption key and MAC key
master_enc_key = hkdf_expand(temp_key, b'enc', 32, hashlib.sha256)
master_mac_key = hkdf_expand(temp_key, b'mac', 32, hashlib.sha256)
```

The HKDF algorithm uses `enc` and `mac` as context parameters, allowing us to derive two very different keys from the same source key.

### Complete Decryption Functions

```python
def decrypt(encrypted_data, enc_key, mac_key):
    """Decrypt Bitwarden encrypted data"""
    version, payload = encrypted_data.split('.', 2)
    if version != '2':
        raise ValueError('Unsupported encryption version')
    fields = payload.split('|')
    if len(fields) != 3:
        raise ValueError('Invalid encrypted data')
    iv = b64decode(fields[0])
    ciphertext = b64decode(fields[1])
    mac = b64decode(fields[2])
    
    # Verify integrity
    calculated_mac = hmac.new(mac_key, iv + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(calculated_mac, mac):
        raise ValueError('Invalid data or key')
    
    # Decrypt
    decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(enc_key, iv))
    return decrypter.feed(ciphertext) + decrypter.feed()

def decrypt_master_key(encrypted_master_key, email, passphrase, iterations=600000):
    """Decrypt master key from passphrase"""
    temp_key = hashlib.pbkdf2_hmac(
        'sha256',
        passphrase.encode(),
        email.encode(),
        iterations,
        32
    )
    master_enc_key = hkdf_expand(temp_key, b'enc', 32, hashlib.sha256)
    master_mac_key = hkdf_expand(temp_key, b'mac', 32, hashlib.sha256)
    return decrypt(encrypted_master_key, master_enc_key, master_mac_key)
```

---

## Complete Interactive Script

Here's the complete script that can decrypt any Bitwarden encrypted data:

```python
import hmac, hashlib, pyaes
from base64 import b64decode
from getpass import getpass

def hkdf_expand(key, info, length, hash_func):
    prk = hmac.new(key, b'bits', hash_func).digest()
    t = b''
    result = b''
    counter = 1
    while len(result) < length:
        t = hmac.new(key, t + info + bytes([counter]), hash_func).digest()
        result += t
        counter += 1
    return result[:length]

def decrypt(encrypted_data, enc_key, mac_key):
    version, payload = encrypted_data.split('.', 2)
    if version != '2':
        raise ValueError('Unsupported encryption version')
    fields = payload.split('|')
    if len(fields) != 3:
        raise ValueError('Invalid encrypted data')
    iv = b64decode(fields[0])
    ciphertext = b64decode(fields[1])
    mac = b64decode(fields[2])
    calculated_mac = hmac.new(mac_key, iv + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(calculated_mac, mac):
        raise ValueError('Invalid data or key')
    decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(enc_key, iv))
    return decrypter.feed(ciphertext) + decrypter.feed()

def decrypt_master_key(encrypted_master_key, email, passphrase, iterations=600000):
    temp_key = hashlib.pbkdf2_hmac('sha256', passphrase.encode(), email.encode(), iterations, 32)
    master_enc_key = hkdf_expand(temp_key, b'enc', 32, hashlib.sha256)
    master_mac_key = hkdf_expand(temp_key, b'mac', 32, hashlib.sha256)
    return decrypt(encrypted_master_key, master_enc_key, master_mac_key)

# Example data
encrypted_master_key = '2.i5dH92a79wJ8L8tsqQEdLw==|a5swb8CeW5cTM2N+XQZCF+mX263BMaag+ghxiu+ci4W+fqqLZ82g+i7ReIcdiPLafoCAmeWZE48PETGJOsoOb6DcrK3sRdvHCx8xbRt1Xas='
encrypted_secret = '2.IkWFb104bXv7Zwl7eFbsnQ==|SB42jIOvjhV32hSusW/J7WfAnQV8DKIV/CJQB7IDaiz4lQv4lIcXzWp9+IT0ncVQ|S8Tcp2klhcOOzZvoA0C9WRURaWUq+U1F9jbuBskDIz0='

email = input('Email address: ')
passphrase = getpass('Passphrase: ')
master_key = decrypt_master_key(encrypted_master_key, email, passphrase)
print(f'Master key: {master_key.hex()}')
print(f'Password: {decrypt(encrypted_secret, master_key[:32], master_key[32:]).decode()}')
```

Example run:
```
Email address: somebody@example.com
Passphrase: the moon landing was fake
Password: The quick brown fox jumps over the lazy dog
```

---

## Encryption: Running Decryption in Reverse

Once you understand decryption, encryption is simple—just run it backwards:

```python
from base64 import b64encode

def encrypt(secret, enc_key, mac_key):
    """Encrypt data"""
    iv = os.urandom(16)  # Random initialization vector
    encrypter = pyaes.Encrypter(pyaes.AESModeOfOperationCBC(enc_key, iv))
    ciphertext = encrypter.feed(secret) + encrypter.feed()
    mac = hmac.new(mac_key, iv + ciphertext, hashlib.sha256).digest()
    return f'2.{b64encode(iv).decode()}|{b64encode(ciphertext).decode()}|{b64encode(mac).decode()}'

def encrypt_master_key(master_key, email, passphrase, iterations=600000):
    """Encrypt master key"""
    temp_key = hashlib.pbkdf2_hmac('sha256', passphrase.encode(), email.encode(), iterations, 32)
    master_enc_key = hkdf_expand(temp_key, b'enc', 32, hashlib.sha256)
    master_mac_key = hkdf_expand(temp_key, b'mac', 32, hashlib.sha256)
    return encrypt(master_key, master_enc_key, master_mac_key)
```

Example for generating a new account:
```python
email = input('Email address: ')
passphrase = getpass('Passphrase: ')
master_key = os.urandom(64)
encrypted_master_key = encrypt_master_key(master_key, email, passphrase)
print(f'Master key: {encrypted_master_key}')
```

If someone gets their hands on your encrypted master key and password, they still need to guess your email and passphrase to decode it. Without those, they simply cannot use the information at all.

---

## Why Bitwarden Chose These Algorithms

| Component | Algorithm | Reason for Choice |
|-----------|-----------|-------------------|
| Key Derivation | PBKDF2-SHA256 | Intentionally slow, increases brute-force cost |
| Iterations | 600,000 | 2026 standard, balancing security and performance |
| Key Stretching | HKDF-SHA256 | Standard HKDF, derive multiple keys from seed |
| Symmetric Encryption | AES-256-CBC | NIST standard, 256-bit key meets highest security requirements |
| Message Authentication | HMAC-SHA256 | Verify integrity, prevent tampering |

**Optional Alternative**: Bitwarden offers the option to switch PBKDF2 to Argon2id. Argon2id is considered more secure but is also more resource-intensive in RAM and computation. I suspect Bitwarden may make Argon2id the default at some point in the future.

---

## Next Steps: Self-Hosting Vaultwarden

This script can serve as the foundation for a complete password decryption solution, designed to work with databases maintained by Vaultwarden without using the Web API or any network functionality.

Next steps you might want to explore:
- How to interact directly with Vaultwarden SQLite database
- How to build your own password management client
- Further enhancements with end-to-end encryption (E2EE)

Feel free to tell me in the comments what other aspects of Bitwarden or Vaultwarden you'd like me to cover!

---

**Reference**: Miguel Grinberg, https://blog.miguelgrinberg.com/post/how-bitwarden-encrypts-and-decrypts-secrets