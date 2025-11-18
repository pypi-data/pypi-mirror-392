import importlib
from pathlib import Path

import typer
from rich.pretty import pretty_repr

from . import __version__
from .logging_invoke import set_logger

SECTION_NAME = 'typer-invoke'


class TyperInvoke(typer.Typer):
    """Typer app that adds invoke configuration."""

    def __init__(self, invoke: dict, **kwargs):
        self.invoke = invoke
        super().__init__(**kwargs)


def get_config() -> dict:
    """Retrieve config from ``pyproject.toml``."""
    from .pyproject import read_package_config

    try:
        config = read_package_config(SECTION_NAME)
    except Exception as e:
        raise ValueError(
            f'Could not read invoke configuration from [b]pyproject.toml[/b]. '
            f'{type(e).__name__}: {e}'
        )

    if not config:
        raise ValueError(
            f'Could not read invoke configuration from [b]pyproject.toml[/b], '
            f'in section [b]{SECTION_NAME}[/b].',
        )

    key = 'modules'
    if key not in config:
        raise ValueError(
            f'Could not find [b]{key}[/b] key in invoke configuration from [b]pyproject.toml[/b], '
            f'in section [b]{SECTION_NAME}[/b].',
        )

    return config


def load_module_app(module_path: str, base_path: str | Path | None = None) -> typer.Typer | None:
    """Load a Typer app from a module path like 'sample.hello'."""
    import sys

    try:
        # Add base_path to sys.path if not already present
        if base_path and str(base_path) not in sys.path:
            sys.path.insert(0, str(base_path))

        module = importlib.import_module(module_path)
        if hasattr(module, 'app') and isinstance(module.app, typer.Typer):
            return module.app
        else:
            typer.echo(
                f'Warning: Module `{module_path}` does not have a Typer app instance named `app`',
                err=True,
            )
            return None
    except ImportError as e:
        typer.echo(f'Could not import module `{module_path}`: {e}', err=True)
        return None


def create_app(
    module_paths: list[str], base_path: str | Path | None = None, **kwargs
) -> typer.Typer:
    """Create a main Typer app with subcommands from specified modules."""
    if not base_path:
        from .pyproject import find_pyproject_toml

        base_path = str(find_pyproject_toml().parent)

    # Defaults for Typer and Invoke
    defaults_typer = dict(
        no_args_is_help=True,
        add_completion=False,
        rich_markup_mode='markdown',
    )

    defaults_invoke = dict(log_level='INFO', log_format='%(message)s')

    # Initialize Invoke, which is just logging configuration
    invoke_kwargs = {k: kwargs.pop(k, v) for k, v in defaults_invoke.items()}
    logger = set_logger(level=invoke_kwargs['log_level'], fmt=invoke_kwargs['log_format'])

    logger.debug(f'typer-invoke {__version__}')
    logger.debug(f'Invoke kwargs: \n{pretty_repr(invoke_kwargs, expand_all=True)}')

    # Initialize Typer
    typer_kwargs = defaults_typer | kwargs
    logger.debug(f'Typer kwargs: \n{pretty_repr(typer_kwargs, expand_all=True)}')
    app = TyperInvoke(invoke=dict(kwargs=invoke_kwargs, logger=logger), **typer_kwargs)

    @app.command(name='help-full', hidden=True, help='Show full help.')
    def show_full_help():
        from rich.console import Console

        from .typer_docs import build_typer_help, extract_typer_info

        typer_info = extract_typer_info(app)
        help_text = build_typer_help(typer_info)
        console = Console()
        console.print(help_text)

    for module_path in module_paths:
        # Extract the module name (last part of the path) to use as subcommand name.
        module_name = module_path.split('.')[-1]

        # Load the module's Typer app
        module_app = load_module_app(module_path, base_path)

        if module_app:
            # Add the module's app as a subcommand group
            app.add_typer(module_app, name=module_name)

    return app


def main():
    """
    Entry point for the invoke CLI.

    Retrieves modules to import from ``pyproject.toml`` and creates a main Typer app.
    """
    config = get_config()
    module_paths = config.pop('modules')
    app = create_app(module_paths, **config)
    app()


if __name__ == '__main__':
    main()
