import urllib.request
from pathlib import Path

from core.exceptions import ImageLoadError

MIME_MAP: dict[str, str] = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
}


def load_image(source: str) -> tuple[bytes, str]:
    """
    Load image bytes and MIME type from a local path or HTTP/HTTPS URL.

    Args:
        source: Local filesystem path or http(s):// URL.

    Returns:
        Tuple of (image_bytes, mime_type).

    Raises:
        ImageLoadError: If the file is not found, the format is unsupported,
            or the URL cannot be fetched.
    """
    if source.startswith(("http://", "https://")):
        return _load_from_url(source)
    return _load_from_path(source)


def _load_from_path(path: str) -> tuple[bytes, str]:
    image_path = Path(path)
    if not image_path.exists():
        raise ImageLoadError(f"Image file not found: {path}")
    mime_type = MIME_MAP.get(image_path.suffix.lower())
    if not mime_type:
        raise ImageLoadError(
            f"Unsupported image format '{image_path.suffix}'. "
            f"Supported: {', '.join(MIME_MAP)}"
        )
    return image_path.read_bytes(), mime_type


def _load_from_url(url: str) -> tuple[bytes, str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Karma-Backend/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:  # noqa: S310
            image_bytes = response.read()
            content_type: str = response.headers.get("Content-Type", "image/jpeg")
            mime_type = content_type.split(";")[0].strip()
        return image_bytes, mime_type
    except Exception as exc:
        raise ImageLoadError(f"Failed to fetch image from URL: {exc}") from exc
