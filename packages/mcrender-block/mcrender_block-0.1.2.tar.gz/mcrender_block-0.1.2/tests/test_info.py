"""Quick test script to verify the test setup works."""

import sys
from pathlib import Path

# Add src to path for direct execution
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tests.conftest import MINECRAFT_VERSION, MINECRAFT_JAR_URL, MINECRAFT_JAR_SHA1

print("=" * 60)
print("VibeCoded MC Renderer - Test Setup Info")
print("=" * 60)
print()
print("Test Configuration:")
print(f"  Minecraft Version: {MINECRAFT_VERSION}")
print(f"  Download URL: {MINECRAFT_JAR_URL}")
print(f"  Expected SHA1: {MINECRAFT_JAR_SHA1}")
print()
print("What happens when you run 'pytest':")
print("  1. Tests check if jar exists in tests/test_data/")
print("  2. If not found, automatically downloads from Mojang")
print("  3. Verifies download with SHA1 hash")
print("  4. Caches jar for future test runs")
print("  5. Runs all tests using the cached jar")
print()
print("To run tests:")
print("  pytest                          # Run all tests")
print("  pytest -v                       # Verbose output")
print("  pytest --cov=vibecoded_mc_renderer  # With coverage")
print()
print("First run will download ~10 MB jar file.")
print("Subsequent runs use cached jar (no download needed).")
print("=" * 60)
