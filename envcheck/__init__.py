"""envcheck: compare .env files against a .env.example template."""
from .core import parse_env, compare

__version__ = "0.1.0"
__all__ = ["parse_env", "compare"]
