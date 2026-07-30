"""Environment settings for pytest."""

import os
import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Forces local development environment variables for all tests."""
    # Force the ENV_MODE to development
    os.environ["ENV_MODE"] = "development"

    # Force load your local database configuration
    load_dotenv(".env.development", override=True)