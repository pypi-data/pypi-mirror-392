#!/usr/bin/env python3
"""
Test with a fresh cache directory to isolate the issue.
"""

import os
import tempfile
import shutil

# Create a fresh temporary cache directory
temp_cache = tempfile.mkdtemp(prefix="fastembed_test_")
print(f"Using fresh cache directory: {temp_cache}")

# Set the cache path
os.environ['FASTEMBED_CACHE_PATH'] = temp_cache
os.environ['RUST_LOG'] = 'debug'

try:
    from competency_api import match_score, init_logging

    init_logging()
    print("\n⏳ Testing with fresh cache (will download model)...")

    result = match_score(
        required_skills=[{"name": "Python", "level": {"value": 3, "max": 5}}],
        candidate_skills=[{"name": "Python", "level": {"value": 3, "max": 5}}]
    )

    print(f"\n✅ SUCCESS! Score: {result['overall_score']:.2%}")
    print(f"\nCache contents:")
    for root, dirs, files in os.walk(temp_cache):
        level = root.replace(temp_cache, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        if level < 3:  # Don't go too deep
            subindent = ' ' * 2 * (level + 1)
            for file in files[:5]:  # Limit files shown
                print(f'{subindent}{file}')

except Exception as e:
    print(f"\n❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Clean up
    print(f"\n🧹 Cleaning up temp cache: {temp_cache}")
    shutil.rmtree(temp_cache, ignore_errors=True)
