"""
synq-ai package has been renamed to [synqed](https://pypi.org/project/synqed/).

This package is deprecated. Please install and use 'synqed' instead:

    pip uninstall synq-ai
    pip install synqed

Then update your imports:

    # Old (deprecated)
    import synq_ai
    
    # New (correct)
    import synqed

For more information, visit: https://synqlabs.ai
"""

import warnings

warnings.warn(
    "The 'synq-ai' package has been renamed to 'synqed'. "
    "Please uninstall 'synq-ai' and install 'synqed' instead: "
    "pip uninstall synq-ai && pip install synqed. "
    "See https://pypi.org/project/synqed/",
    DeprecationWarning,
    stacklevel=2
)

__version__ = "1.0.1"

