import os
import time
import gc
import logging
import threading
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def cleanup_memory():
    """Force garbage collection and report memory usage"""
    collected = gc.collect()
    
    if PSUTIL_AVAILABLE:
        try:
            process = psutil.Process(os.getpid())
            memory_usage = process.memory_info().rss / 1024 / 1024
            logging.info("Memory cleanup: collected %s objects, current usage: %.2f MB", collected, memory_usage)
            return memory_usage
        except Exception as e:
            logging.error("Error getting memory info: %s", e)
    else:
        logging.info("Memory cleanup: collected %s objects", collected)
    
    return collected


def cleanup_old_files(upload_folder=None, max_age_hours=24):
    """Remove files older than max_age_hours from the uploads folder"""
    if upload_folder is None:
        try:
            from flask import current_app
            upload_folder = current_app.config.get('UPLOAD_FOLDER')
        except Exception:
            upload_folder = None
        if not upload_folder:
            try:
                import app as _app_mod
                upload_folder = _app_mod.app.config.get('UPLOAD_FOLDER', 'static/uploads')
            except Exception:
                upload_folder = 'static/uploads'

    current_time = datetime.now()
    upload_dir = upload_folder
    
    deleted_count = 0
    total_bytes_recovered = 0
    
    if not os.path.exists(upload_dir):
        return deleted_count, total_bytes_recovered

    try:
        for filename in os.listdir(upload_dir):
            if filename == 'README.md':
                continue
                
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                age_hours = (current_time - file_time).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    try:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted_count += 1
                        total_bytes_recovered += file_size
                        logging.info("Removed old file: %s (%.1f KB)", filename, file_size / 1024)
                    except Exception as e:
                        logging.error("Error removing file %s: %s", filename, e)
    except Exception as e:
        logging.error("Error during cleanup: %s", e)
    
    # Also clean the cache directory
    cache_dir = os.path.join(upload_dir, 'cache')
    if os.path.exists(cache_dir):
        try:
            for filename in os.listdir(cache_dir):
                file_path = os.path.join(cache_dir, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    age_hours = (current_time - file_time).total_seconds() / 3600
                    
                    if age_hours > max_age_hours:
                        try:
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            deleted_count += 1
                            total_bytes_recovered += file_size
                            logging.info("Removed old cache file: %s (%.1f KB)", filename, file_size / 1024)
                        except Exception as e:
                            logging.error("Error removing cache file %s: %s", filename, e)
        except Exception as e:
            logging.error("Error cleaning cache: %s", e)
    
    return deleted_count, total_bytes_recovered


def _cleanup_settings():
    """Read the cleanup schedule from the environment, with safe fallbacks."""
    def _positive_float(name, default):
        try:
            value = float(os.environ.get(name, default))
        except (TypeError, ValueError):
            logging.warning("Invalid %s - falling back to %s", name, default)
            return default
        if value <= 0:
            logging.warning("%s must be positive - falling back to %s", name, default)
            return default
        return value

    return (
        _positive_float('BRANDKIT_CLEANUP_INTERVAL_HOURS', 1.0),
        _positive_float('BRANDKIT_RETENTION_HOURS', 24.0),
    )


def start_cleanup_thread(upload_folder=None):
    """Start the periodic upload/cache cleanup background worker thread.

    Controlled explicitly by application initialization or server startup entrypoints.
    Set BRANDKIT_CLEANUP_ENABLED=false to opt out.
    """
    if os.environ.get('BRANDKIT_CLEANUP_ENABLED', 'true').lower() in ('0', 'false', 'no'):
        logging.info("Scheduled cleanup disabled via BRANDKIT_CLEANUP_ENABLED")
        return None

    interval_hours, retention_hours = _cleanup_settings()

    def scheduled_cleanup():
        while True:
            time.sleep(interval_hours * 3600)
            try:
                cleanup_old_files(upload_folder=upload_folder, max_age_hours=retention_hours)
                cleanup_memory()
            except Exception:
                logging.exception("Scheduled cleanup failed")

    thread = threading.Thread(
        target=scheduled_cleanup, name='brandkit-cleanup', daemon=True
    )
    thread.start()
    logging.info(
        "Scheduled cleanup started: every %sh, deleting files older than %sh",
        interval_hours, retention_hours
    )
    return thread
