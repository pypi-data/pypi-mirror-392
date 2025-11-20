#!/usr/bin/env python3
"""Debug script to test model initialization."""

import os
import sys

# Enable detailed error messages
os.environ['RUST_BACKTRACE'] = '1'

print("=" * 60)
print("Testing Embedding Model Initialization")
print("=" * 60)

try:
    from competency_api import match_score, init_logging

    print("\n✓ Module imported successfully")

    # Enable logging to see what's happening
    init_logging()
    print("✓ Logging initialized")

    # Try a simple match
    print("\n⏳ Attempting to run match_score...")
    print("   This will download ~100MB model on first run...")

    result = match_score(
        required_skills=[{"name": "Python", "level": {"value": 3, "max": 5}}],
        candidate_skills=[{"name": "Python", "level": {"value": 3, "max": 5}}]
    )

    print("\n✓ Match completed successfully!")
    print(f"   Score: {result['overall_score']:.2%}")

except Exception as e:
    print(f"\n✗ Error occurred: {type(e).__name__}")
    print(f"   Message: {e}")
    print("\n" + "=" * 60)
    print("Troubleshooting Steps:")
    print("=" * 60)
    print("1. Check internet connection")
    print("2. Try setting a custom cache directory:")
    print("   export FASTEMBED_CACHE_PATH=/tmp/fastembed_cache")
    print("3. Check HuggingFace access (https://huggingface.co)")
    print("4. Verify disk space (~200MB needed)")
    print("\nFull error details:")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("All tests passed! Model is working correctly.")
print("=" * 60)
