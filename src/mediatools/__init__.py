"""Compatibility wrapper for the unified videoedit backend."""

import warnings

from ._videoedit_bootstrap import ensure_videoedit_on_path

ensure_videoedit_on_path()

warnings.warn(
    "mediatools is deprecated and now acts as a compatibility wrapper. "
    "Use 'videoedit' for new code.",
    FutureWarning,
    stacklevel=2,
)

from videoedit.media import *  # noqa: F401,F403
