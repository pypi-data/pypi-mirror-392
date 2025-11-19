"""
MediCafe/api_hints.py

Lightweight, XP/Python 3.4.4 compatible helpers to emit concise console hints
for common network/DNS issues and 404 route mismatches. No dependencies; avoid
PHI/PII; intended to be called from exception handlers only.
"""

import sys
import time
import subprocess

# Optional import for requests (may not be available in all contexts)
try:
    import requests
except ImportError:
    requests = None

# Module-level cache for connectivity check results
_connectivity_cache = {'result': None, 'timestamp': 0}
_CONNECTIVITY_CACHE_TTL = 30  # Cache for 30 seconds to avoid redundant checks


def _safe_print(message, console):
    """Print only when console is True; guard against unexpected stdout issues."""
    if not console:
        return
    try:
        # Avoid encoding crashes on legacy consoles
        sys.stdout.write(str(message) + "\n")
        sys.stdout.flush()
    except Exception:
        try:
            print(str(message))
        except Exception:
            pass


def _normalize_text(value):
    try:
        return (value or "").strip().lower()
    except Exception:
        try:
            return str(value).strip().lower()
        except Exception:
            return ""


def _is_likely_dns_or_connectivity_error(error_text):
    text = _normalize_text(error_text)
    # Broad but safe indicators seen from urllib3/requests/socket layers
    patterns = [
        "getaddrinfo failed",                    # DNS resolution failure (Windows errno 11001)
        "name or service not known",             # *nix DNS failure
        "nodename nor servname provided",
        "temporary failure in name resolution",
        "failed to establish a new connection",  # connection-level failure
        "max retries exceeded with url",         # transport retries exhausted
        "connection aborted",
        "connection refused",
        "timed out",
        "certificate verify failed"              # network path ok but TLS chain issue
    ]
    for p in patterns:
        if p in text:
            return True
    return False


def _check_internet_connectivity_cached():
    """
    Check internet connectivity with 30-second TTL cache to avoid redundant checks.
    
    Returns:
        tuple: (is_connected (bool), was_cached (bool))
    
    Uses requests.get() to lightweight endpoint first, falls back to ping if requests
    unavailable. Caches result for 30 seconds to avoid redundant network calls when
    multiple API failures occur in quick succession.
    """
    global _connectivity_cache
    
    try:
        current_time = time.time()
        cache_age = current_time - _connectivity_cache['timestamp']
        
        # Return cached result if still valid (within TTL)
        if _connectivity_cache['result'] is not None and cache_age < _CONNECTIVITY_CACHE_TTL:
            return (_connectivity_cache['result'], True)
        
        # Check connectivity using requests if available (fastest method)
        if requests is not None:
            try:
                # Use lightweight endpoint with short timeout (Google is reliable)
                # Any response (even 4xx/5xx) indicates connectivity - only exceptions indicate no connectivity
                requests.get('http://www.google.com', timeout=2, allow_redirects=False)
                is_connected = True
            except Exception:
                # If request fails (timeout, connection error, etc.), assume no connectivity
                is_connected = False
        else:
            # Fallback to ping if requests unavailable (Windows: ping -n 1)
            try:
                # Use subprocess ping - Windows compatible (XP compatible)
                # Use timeout to prevent hanging (Python 3.3+ supports timeout parameter)
                ping_process = subprocess.Popen(
                    ['ping', '-n', '1', '8.8.8.8'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                # Wait up to 5 seconds for ping to complete (Windows ping typically completes in 2-4 seconds)
                # Timeout parameter available in Python 3.3+ (this codebase targets 3.4.4)
                try:
                    ping_process.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    # If ping times out, kill it and assume no connectivity
                    ping_process.kill()
                    ping_process.communicate()  # Clean up
                    is_connected = False
                else:
                    # Check if ping was successful (returncode 0 indicates success)
                    is_connected = ping_process.returncode == 0
            except Exception:
                is_connected = False
        
        # Update cache with result and timestamp
        _connectivity_cache['result'] = is_connected
        _connectivity_cache['timestamp'] = current_time
        
        return (is_connected, False)
        
    except Exception:
        # On any exception, assume no connectivity and don't cache (allow retry)
        return (False, False)


def emit_network_hint(endpoint_name, target_url, exception_obj, console=False):
    """
    Emit a concise network/proxy/DNS troubleshooting hint with automatic connectivity check.

    Parameters:
        endpoint_name (str): Logical endpoint (e.g., 'UHCAPI', 'OPTUMAI')
        target_url (str): URL attempted
        exception_obj (Exception): The original exception
        console (bool): If True, prints to console
    """
    try:
        err_text = str(exception_obj)
    except Exception:
        err_text = ""

    # Only emit on probable network/DNS classes; keep messages brief and generic.
    if not _is_likely_dns_or_connectivity_error(err_text):
        return

    try:
        # Check internet connectivity (cached for 30 seconds to avoid redundant checks)
        is_connected, _ = _check_internet_connectivity_cached()
        
        _safe_print("[Connectivity hint] {} call to {} appears to have failed before authentication.".format(endpoint_name, target_url), console)
        
        # Provide context-specific guidance based on connectivity status
        if not is_connected:
            _safe_print("Internet connectivity issue detected - check network connection.", console)
            _safe_print("Verify internet connection: ping 8.8.8.8 or check network adapter status.", console)
        else:
            _safe_print("Internet appears connected - issue may be DNS/proxy/firewall specific to this endpoint.", console)
            _safe_print("This often indicates DNS/proxy/firewall issues rather than an OAuth problem.", console)
            _safe_print("Quick checks (Windows): nslookup host; Test-NetConnection host -Port 443;", console)
        
        _safe_print("If issues persist: ipconfig /flushdns; netsh winsock reset; netsh int ip reset;", console)
        _safe_print("Also verify proxy: netsh winhttp show proxy (or set HTTPS_PROXY env for this process).", console)
        _safe_print("Note: Do not include PHI/PII in any shared logs.", console)
    except Exception:
        # Best-effort only; never raise from hinting.
        pass


def emit_404_route_hint(method, url, status_code, response_content, console=False):
    """
    Emit a concise route/path troubleshooting hint for provider 404s that say
    "no Route matched with those values".
    """
    try:
        if int(status_code) != 404:
            return
    except Exception:
        return

    try:
        body_text = _normalize_text(response_content)
        if not body_text:
            return
        if ("no route matched" not in body_text) and ("no route" not in body_text):
            return
    except Exception:
        return

    try:
        _safe_print("[Route hint] {} {} returned 404 'no route matched'.".format(method, url), console)
        _safe_print("Verify endpoint path in config, and ensure no double/missing slashes in URL join.", console)
        _safe_print("Providers may deprecate paths; compare with latest swagger/docs.", console)
        _safe_print("Also check unintended environment headers influencing routing (e.g., 'env: sandbox').", console)
    except Exception:
        pass


