#!/bin/bash
set -e

# Ensure static/uploads exists
mkdir -p static/uploads

# Run Flask app
exec python app.py
