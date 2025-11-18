def string():
    """Get version string from setuptools_scm generated file."""
    try:
        from qsimkit._version import __version__
        return __version__
    except ImportError:
        # Fallback for development environments
        try:
            import os
            with open(os.path.dirname(__file__) + "/VERSION", "r", encoding="utf-8") as fh:
                version = fh.read().strip()
                if version:
                    return version
        except:
            pass
        return "unknown"