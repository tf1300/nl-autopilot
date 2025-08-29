# Secrets

This directory contains secrets encrypted with SOPS. They are decrypted at runtime by Docker Compose.

To edit secrets, use `sops` with the appropriate age key:

```bash
sops secrets/aead_key.enc
```
