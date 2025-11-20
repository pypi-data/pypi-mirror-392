#!/usr/bin/env python3
"""
Diagnostic script to debug embedding model issues.
Run this in the environment where you're having problems.
"""

import sys
import os

print("=" * 70)
print("COMPETENCY API - ENVIRONMENT DIAGNOSTICS")
print("=" * 70)

# 1. Python version
print(f"\n1. Python Version:")
print(f"   {sys.version}")
print(f"   Executable: {sys.executable}")

# 2. Check if competency_api is installed
print(f"\n2. Checking competency_api installation:")
try:
    import competency_api
    print(f"   ✓ competency_api is installed")
except ImportError as e:
    print(f"   ✗ competency_api NOT installed: {e}")
    print(f"\n   Install with: pip install /path/to/competency_api-*.whl")
    sys.exit(1)

# 3. Check cache directory
print(f"\n3. Cache Directory:")
cache_dir = os.environ.get('FASTEMBED_CACHE_PATH', os.path.expanduser('~/.cache/fastembed'))
print(f"   Path: {cache_dir}")
print(f"   Exists: {os.path.exists(cache_dir)}")
if os.path.exists(cache_dir):
    print(f"   Contents: {os.listdir(cache_dir)}")
parent_dir = os.path.dirname(cache_dir)
print(f"   Parent writable: {os.access(parent_dir, os.W_OK)}")

# 4. Check disk space
print(f"\n4. Disk Space:")
try:
    import shutil
    total, used, free = shutil.disk_usage("/")
    print(f"   Free space: {free // (2**30)} GB")
    if free < 500 * 1024 * 1024:  # Less than 500MB
        print(f"   ⚠ WARNING: Low disk space!")
except Exception as e:
    print(f"   Could not check: {e}")

# 5. Test network connectivity to HuggingFace
print(f"\n5. Network Connectivity:")
try:
    import urllib.request
    response = urllib.request.urlopen('https://huggingface.co', timeout=5)
    print(f"   ✓ Can reach huggingface.co (status: {response.status})")
except Exception as e:
    print(f"   ✗ Cannot reach huggingface.co: {e}")
    print(f"   ⚠ Model download will fail without internet access")

# 6. Try to import and run a simple test
print(f"\n6. Testing Competency API:")
try:
    from competency_api import match_score, init_logging

    print(f"   ✓ Functions imported successfully")
    print(f"   ⏳ Running test match (will download ~100MB model on first run)...")
    print(f"      This may take 30-60 seconds on first run...")

    # Set verbose logging
    os.environ['RUST_LOG'] = 'info'
    init_logging()

    result = match_score(
        required_skills=[{"name": "Test", "level": {"value": 1, "max": 5}}],
        candidate_skills=[{"name": "Test", "level": {"value": 1, "max": 5}}]
    )

    print(f"   ✓ Test completed successfully!")
    print(f"   ✓ Overall score: {result['overall_score']:.2%}")

except RuntimeError as e:
    print(f"   ✗ RuntimeError: {e}")
    print(f"\n" + "=" * 70)
    print("POSSIBLE SOLUTIONS:")
    print("=" * 70)

    if "Failed to retrieve" in str(e):
        print("\n📥 Model Download Failed")
        print("   Causes:")
        print("   - No internet connection")
        print("   - Firewall blocking huggingface.co")
        print("   - Proxy configuration needed")
        print("   - HuggingFace server issues")
        print("\n   Solutions:")
        print("   1. Check internet connection")
        print("   2. Try setting a custom cache directory:")
        print("      export FASTEMBED_CACHE_PATH=/tmp/fastembed_cache")
        print("   3. If behind a proxy, set HTTP_PROXY and HTTPS_PROXY")
        print("   4. Try manual download:")
        print("      mkdir -p ~/.cache/fastembed")
        print("      # Then copy model files if available from another machine")

    elif "Permission denied" in str(e):
        print("\n🔒 Permission Error")
        print("   Solutions:")
        print("   1. Check directory permissions:")
        print(f"      chmod -R u+w {cache_dir}")
        print("   2. Use a different cache directory:")
        print("      export FASTEMBED_CACHE_PATH=/tmp/fastembed_cache")

    else:
        print(f"\n❓ Unknown error: {e}")
        print("   Try enabling verbose logging:")
        print("      export RUST_LOG=debug")
        print("      export RUST_BACKTRACE=full")

    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)

except Exception as e:
    print(f"   ✗ Unexpected error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ ALL DIAGNOSTICS PASSED")
print("=" * 70)
print("\nThe competency_api package is working correctly in this environment!")
