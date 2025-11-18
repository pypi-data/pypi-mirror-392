import pytest
from rich.console import Console

from typer_invoke.logging_invoke import get_logger, set_logger


@pytest.fixture(scope='session')
def console():
    return Console(stderr=True, force_terminal=True)


@pytest.fixture(scope='session')
def logger():
    set_logger()
    return get_logger()
