#!/usr/bin/env python3
"""
build_deductible_cache.py

Silent helper that runs MediLink_Deductible_v1_5 during CSV intake so that the
insurance_type_cache.json gets populated without requiring any additional user
interaction. Designed to be invoked from process_csvs.bat immediately after a
fresh CSV is moved into place (Email de Carol flow).
"""

from __future__ import print_function

import argparse
import os
import sys
import traceback

# Ensure workspace root is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.dirname(CURRENT_DIR)
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from MediCafe.core_utils import get_shared_config_loader  # noqa: E402

try:
    from MediLink.MediLink_Deductible_v1_5 import run_batch_from_csv  # noqa: E402
except Exception as import_err:  # pragma: no cover - guard rails for XP envs
    print("Deductible cache builder: cannot import v1.5 module: {}".format(import_err))
    sys.exit(1)

try:
    from MediLink.MediLink_Up import check_internet_connection  # noqa: E402
except Exception:
    check_internet_connection = None


LOGGER = get_shared_config_loader()


def _log(message, level="INFO"):
    """Best-effort logging via shared config loader, falling back to print."""
    try:
        if LOGGER and hasattr(LOGGER, "log"):
            LOGGER.log(message, level=level)
            return
    except Exception:
        pass
    try:
        print(message)
    except Exception:
        pass


def _clear_cached_configuration():
    """Ensure subsequent loads read the freshly updated config file."""
    try:
        from MediCafe import MediLink_ConfigLoader
        clear_func = getattr(MediLink_ConfigLoader, "clear_config_cache", None)
        if callable(clear_func):
            clear_func()
    except Exception:
        pass


def _load_config():
    """Load the latest configuration dictionary (after clearing cache)."""
    config = {}
    try:
        if LOGGER and hasattr(LOGGER, "load_configuration"):
            _clear_cached_configuration()
            config, _ = LOGGER.load_configuration()
    except Exception as exc:
        _log("Deductible cache builder: failed to load config ({})".format(exc), level="WARNING")
        config = {}
    return config or {}


def _has_internet():
    """Return True when internet connectivity is available (best effort)."""
    if check_internet_connection is None:
        return True
    try:
        return bool(check_internet_connection())
    except Exception as exc:
        _log("Deductible cache builder: connectivity check failed ({}) – continuing as online.".format(exc), level="WARNING")
        return True


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Silent helper that builds the insurance type cache using MediLink_Deductible_v1_5."
    )
    parser.add_argument(
        "--skip-internet-check",
        action="store_true",
        help="Run even when connectivity check fails."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print a short summary to stdout even when logger is available."
    )
    return parser.parse_args()


def main():
    args = _parse_args()

    if not args.skip_internet_check and not _has_internet():
        _log("Deductible cache builder: skipped (offline).", level="INFO")
        return 0

    config = _load_config()
    csv_path = ""
    try:
        csv_path = config.get("CSV_FILE_PATH", "")
    except Exception:
        csv_path = ""

    if not csv_path:
        _log("Deductible cache builder: no CSV_FILE_PATH configured; nothing to do.", level="INFO")
        return 0

    if not os.path.exists(csv_path):
        _log("Deductible cache builder: CSV not found at '{}'; skipping cache build.".format(csv_path), level="INFO")
        return 0

    _log("Deductible cache builder: starting silent batch against '{}'.".format(csv_path), level="INFO")

    try:
        results = run_batch_from_csv(config)
        processed_count = len(results or [])
        summary = "Deductible cache builder: completed – {} patient(s) refreshed.".format(processed_count)
        _log(summary, level="INFO")
        if args.verbose:
            print(summary)
        return 0
    except Exception as exc:  # pragma: no cover - protective logging for runtime failures
        _log("Deductible cache builder: failed with error: {}".format(exc), level="ERROR")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
