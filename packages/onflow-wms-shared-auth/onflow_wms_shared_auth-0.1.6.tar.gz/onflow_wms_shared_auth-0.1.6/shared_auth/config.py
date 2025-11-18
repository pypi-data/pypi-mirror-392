import os
from datetime import timedelta

# --- JWT / Token settings ---
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
TOKEN_OPS = os.environ.get("TOKEN_OPS")

# --- Token lifetime ---
ACCESS_TOKEN_LIFETIME = timedelta(
    hours=int(os.environ.get("ACCESS_TOKEN_HOURS", 48))
)
REFRESH_TOKEN_LIFETIME = timedelta(
    days=int(os.environ.get("REFRESH_TOKEN_DAYS", 7))
)

# --- Optional: logging helper ---
def print_config_summary():
    """Prints non-sensitive config summary for debugging"""
    print("✅ Onflow Shared Auth configuration loaded:")
    print(f"- SECRET_KEY: {'*' * 10 if SECRET_KEY else 'Not Set'}")
    print(f"- ALGORITHM: {ALGORITHM}")
    print(f"- TOKEN_OPS: {'*' * 6 if TOKEN_OPS else 'Not Set'}")
    print(f"- ACCESS_TOKEN_LIFETIME: {ACCESS_TOKEN_LIFETIME}")
    print(f"- REFRESH_TOKEN_LIFETIME: {REFRESH_TOKEN_LIFETIME}")
