"""The tremors package."""

from tremors.decorator import from_logged, logged
from tremors.logger import EXTRA_KEY, Collector, Logger

__authors__ = ["Narvin Singh"]
__project__ = "Tremors"
__version__ = "0.3.2"

__all__ = ["EXTRA_KEY", "Collector", "Logger", "__version__", "from_logged", "logged"]
