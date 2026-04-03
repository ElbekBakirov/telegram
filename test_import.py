import traceback
import sys

try:
    print("Testing bot import...")
    import bot
    print("Import successful!")
except Exception:
    print("Import failed! Traceback:")
    traceback.print_exc()
    sys.exit(1)
