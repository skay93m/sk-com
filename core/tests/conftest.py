# env vars are set in settings.py (TESTING fallback) — no setup needed here.
import pytest
import core.labs as labs_module


# Concept: test isolation — module-level caches persist between tests in the
# same process. This fixture resets them before and after each test so that
# one test's filesystem state cannot bleed into another's.
@pytest.fixture(autouse=True)
def reset_labs_cache():
    labs_module._cache = None
    labs_module._projects_cache = None
    yield
    labs_module._cache = None
    labs_module._projects_cache = None
