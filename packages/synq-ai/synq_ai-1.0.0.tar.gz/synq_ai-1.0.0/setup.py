"""Setup configuration for synq-ai (deprecated, redirects to synqed)."""

from setuptools import setup, find_packages

setup(
    name="synq-ai",
    version="1.0.0",
    author="Synq Team",
    author_email="support@synq.dev",
    description="[DEPRECATED] This package has been renamed to 'synqed'. Please use 'synqed' instead.",
    long_description="""
# synq-ai is now synqed

This package has been renamed to **synqed**.

## Migration

synq-ai package has been renamed to synqed.

This package is deprecated. Please install and use 'synqed' instead:

    pip uninstall synq-ai
    pip install synqed

Then update your imports:

    # Old (deprecated)
    import synq_ai
    
    # New (correct)
    import synqed

For more information, visit: https://synqlabs.ai

This package will no longer receive updates. All future development happens in the `synqed` package.
    """,
    long_description_content_type="text/markdown",
    url="https://synqlabs.ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 7 - Inactive",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[],  # No dependencies, just a stub
    keywords="deprecated synq synqed",
)

