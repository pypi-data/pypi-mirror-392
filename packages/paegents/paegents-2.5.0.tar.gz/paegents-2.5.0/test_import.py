#!/usr/bin/env python3
"""
Test script to verify the paegents SDK can be imported and used.
Run: python3 test_import.py
"""

from paegents import PaegentsSDK

# Test 1: SDK instantiation
sdk = PaegentsSDK(
    api_key='ak_test_123',
    agent_id='test-agent',
    api_url='http://localhost:8000'
)

print("✅ SDK Import Test Passed!")
print(f"   Version: {sdk.__class__.__module__}")
print(f"   Agent ID: {sdk.agent_id}")
print(f"   API URL: {sdk.api_url}")
print()

# Test 2: List available methods
methods = [m for m in dir(sdk) if not m.startswith('_') and callable(getattr(sdk, m))]
print(f"✅ Found {len(methods)} available methods:")
for method in sorted(methods)[:15]:
    print(f"   - {method}()")

print()
print("✅ All tests passed! The SDK is ready to use.")
