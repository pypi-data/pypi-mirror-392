import logging

# Configure library-wide logger but overridable by the root logger in the consuming code.
logger = logging.getLogger(__name__)
logger.propagate = True  # Allow log messages to propagate to root logger

from .source import commands, store
from .source.commands import base
from .source.ssh import Ssh
from .source.ssh_key import SshKey

__all__ = ["Ssh", "SshKey", "commands", "base", "store"]
