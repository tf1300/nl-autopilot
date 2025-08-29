#!/bin/bash
set -e

# Debugging: Check listening ports before running the Python script
netstat -tulnp

python decoder_service.py