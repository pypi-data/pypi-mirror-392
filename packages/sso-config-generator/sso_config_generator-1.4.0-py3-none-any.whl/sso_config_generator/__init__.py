"""SSO Config Generator - Generate AWS SSO configuration and directory structures."""

from .version import __version__
from .core import SSOConfigGenerator

__all__ = ["SSOConfigGenerator", "__version__"]
