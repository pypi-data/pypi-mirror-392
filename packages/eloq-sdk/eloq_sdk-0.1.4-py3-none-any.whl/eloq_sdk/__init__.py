from .client import EloqAPI
from .__version__ import __version__
from .exceptions import EloqAPIError


def from_environ():
    """Create a EloqAPI instance from environment variables."""

    return EloqAPI.from_environ()


def from_key(key):
    """Create a EloqAPI instance from a key."""

    return EloqAPI.from_key(key)


def from_key_and_url(key, url):
    """Create a EloqAPI instance from a key and URL."""

    return EloqAPI.from_key_and_url(key, url)
