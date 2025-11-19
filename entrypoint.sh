#!/bin/bash
set -e

# Ensure static/uploads exists
mkdir -p static/uploads

# Default port
PORT=${PORT:-8000}

# If gunicorn is installed, use it (production-ready)
if command -v gunicorn > /dev/null 2>&1; then
  echo "Starting with gunicorn on 0.0.0.0:${PORT}"
  exec gunicorn --bind 0.0.0.0:${PORT} --worker-tmp-dir /dev/shm "app:app"
fi

# If flask CLI is available and FLASK_APP is set, use it
if command -v flask > /dev/null 2>&1 && [ -n "${FLASK_APP:-}" ]; then
  echo "Starting with flask CLI on 0.0.0.0:${PORT}"
  exec flask run --host=0.0.0.0 --port=${PORT}
fi

# Last-resort: import the app module and run it with host=0.0.0.0
# This assumes your app module is named `app.py` and exposes a WSGI object named `app`.
echo "Falling back to python module run (forcing host=0.0.0.0:${PORT})"
python - <<PY
import os
import importlib
port = int(os.environ.get("PORT", ${PORT}))
mod = importlib.import_module("app")
# common names: app, application
if hasattr(mod, "app"):
    server_app = getattr(mod, "app")
elif hasattr(mod, "application"):
    server_app = getattr(mod, "application")
else:
    raise SystemExit("Could not find 'app' or 'application' in app.py")
# If it's a Flask app, call run with host=0.0.0.0
try:
    server_app.run(host="0.0.0.0", port=port)
except Exception as e:
    import traceback
    traceback.print_exc()
    raise SystemExit(1)
PY