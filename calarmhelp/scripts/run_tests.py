"""Script to run tests for calarmhelp."""

import pytest


def run():
    """Run pytest with coverage report."""
    pytest.main(["--cov=calarmhelp", "--cov-report=term-missing"])


if __name__ == "__main__":
    run()
