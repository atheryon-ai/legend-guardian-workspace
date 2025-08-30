"""Legend Guardian main package."""

# Only import settings when the package is fully imported
__all__ = ["settings"]

def __getattr__(name):
    if name == "settings":
        from legend_guardian.config import settings
        return settings
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")