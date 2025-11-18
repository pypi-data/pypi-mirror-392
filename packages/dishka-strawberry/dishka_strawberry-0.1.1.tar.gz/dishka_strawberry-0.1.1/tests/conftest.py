import pytest
from dishka import (
    AsyncContainer,
    Container,
    make_async_container,
    make_container,
)

from .common import AppProvider


@pytest.fixture
def app_provider() -> AppProvider:
    return AppProvider()


@pytest.fixture
def async_container(app_provider: AppProvider) -> AsyncContainer:
    return make_async_container(app_provider)


@pytest.fixture
def container(app_provider: AppProvider) -> Container:
    return make_container(app_provider)
