---
id: "cedf8ac5-92e6-46fb-9f02-af9b79881fb3"
name: "Implement Salsa20/12 encryption/decryption with interactive prompts"
description: "Implement Salsa20/12 cipher supporting 64/128/256-bit keys with interactive input prompts. Accepts key length, key (hex), nonce (hex), and text (hex). Validates key/nonce lengths. Uses specific constants: 'expand 08-byte k' for 64-bit, 'expand 16-byte k' for 128-bit, 'expand 32-byte k' for 256-bit. Constructs 64-byte state per Salsa20 spec: constants[0:4] + key[0:4] + key[4:8] + constants[4:8] + nonce + constants[8:12] + key[8:12] + key[12:16] + constants[12:16]. Processes data in 64-byte blocks, generates keystream via 12 rounds (6 double-rounds), XORs with keystream, outputs result as hex. Includes input validation and error handling."
version: "0.1.0"
tags:
  - "cryptography"
  - "salsa20"
  - "encryption"
  - "interactive"
triggers:
  - "implement salsa20 encryption"
  - "salsa20 12 cipher"
  - "salsa20/12 encrypt"
  - "salsa20/12 decrypt"
  - "salsa20 12 implementation"
---

# Implement Salsa20/12 encryption/decryption with interactive prompts

Implement Salsa20/12 cipher supporting 64/128/256-bit keys with interactive input prompts. Accepts key length, key (hex), nonce (hex), and text (hex). Validates key/nonce lengths. Uses specific constants: 'expand 08-byte k' for 64-bit, 'expand 16-byte k' for 128-bit, 'expand 32-byte k' for 256-bit. Constructs 64-byte state per Salsa20 spec: constants[0:4] + key[0:4] + key[4:8] + constants[4:8] + nonce + constants[8:12] + key[8:12] + key[12:16] + constants[12:16]. Processes data in 64-byte blocks, generates keystream via 12 rounds (6 double-rounds), XORs with keystream, outputs result as hex. Includes input validation and error handling.

## Prompt

Implement Salsa20/12 with interactive prompts for key length, key, nonce, and text. Validate key length is 64/128/256 bits. Ensure key and nonce are correct byte lengths. Output result as hex string.

## Triggers

- implement salsa20 encryption
- salsa20 12 cipher
- salsa20/12 encrypt
- salsa20/12 decrypt
- salsa20 12 implementation
