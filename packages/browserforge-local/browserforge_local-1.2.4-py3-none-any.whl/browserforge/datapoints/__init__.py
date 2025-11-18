from pathlib import Path

DATA_DIR: Path = Path(__file__).parent / "data"

def _fallback(path: Path, loader_name: str):
    if path.exists():
        return path
    try:
        from apify_fingerprint_datapoints import __dict__ as upstream
        return upstream[loader_name]()
    except Exception:
        return path

def get_input_network() -> Path:
    return _fallback(DATA_DIR / "input-network.zip", "get_input_network")

def get_header_network() -> Path:
    return _fallback(DATA_DIR / "header-network.zip", "get_header_network")

def get_fingerprint_network() -> Path:
    return _fallback(DATA_DIR / "fingerprint-network.zip", "get_fingerprint_network")

def get_headers_order() -> Path:
    return _fallback(DATA_DIR / "headers-order.json", "get_headers_order")

def get_browser_helper_file() -> Path:
    return _fallback(DATA_DIR / "browser-helper-file.json", "get_browser_helper_file")

__all__ = [
    "get_input_network",
    "get_header_network",
    "get_fingerprint_network",
    "get_headers_order",
    "get_browser_helper_file",
]