"""
Re-exports :func:`reverse_complement` from :mod:`bioseq_toolkit.core.sequence`.

The implementation lives in the core module; this module exists so that
callers can import from a semantically meaningful path:

    from bioseq_toolkit.utils.reverse_complement import reverse_complement
"""

from bioseq_toolkit.core.sequence import reverse_complement

__all__ = ["reverse_complement"]
