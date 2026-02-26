"""
Test to verify the testing framework setup is working correctly.
"""
import pytest
from hypothesis import given, strategies as st


@pytest.mark.unit
def test_pytest_working():
    """Verify pytest is working correctly."""
    assert True, "Pytest is working!"


@pytest.mark.property
@given(st.integers())
def test_hypothesis_working(x):
    """Verify Hypothesis property-based testing is working correctly."""
    # Property: adding zero to any integer returns the same integer
    assert x + 0 == x, "Hypothesis is working!"


@pytest.mark.unit
def test_imports():
    """Verify all required libraries can be imported."""
    try:
        import librosa
        import hypothesis
        import pytest
        import sounddevice
        
        assert True, "All core imports successful!"
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")
