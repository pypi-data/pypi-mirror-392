
# company/__init__.py

# Import the main class for easy access
from .gbm_simulation import GBMSimulator

# Import version information for the package
from .version import __version__  # Ensure version.py contains this variable

# Print the package version for confirmation (optional)
print(f"Package version: {__version__}")