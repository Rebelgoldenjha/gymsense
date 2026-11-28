#!/usr/bin/env python3
"""Convenience test runner delegating to tests/test_pose_analyzer.py."""

import tests.test_pose_analyzer as suite

if __name__ == "__main__":
    for name, fn in list(vars(suite).items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  [PASS] {name}")
    print("ALL TESTS PASSED!")
