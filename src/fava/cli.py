"""The command-line interface for Fava."""

from __future__ import annotations

import errno
import os
import sys
from pathlib import Path

import click
from cheroot.wsgi import Server
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.middleware.profiler import ProfilerMiddleware

from fava import __version__
from fava.application import create_app
from fava.util import setup_debug_logging
from fava.util import simple_wsgi


class AddressInUse(click.ClickException):  # noqa: D101
    def __init__(self, port: int) -> None:  # pragma: no cover
        super().__init__(
            f"Cannot start Fava because port {port} is already in use."
            "\nPlease choose a different port with the '-p' option.",
        )


class NonAbsolutePathError(click.UsageError):  # noqa: D101
    def __init__(self, path: str) -> None:
        super().__init__(
            f"Paths in BEANCOUNT_FILE need to be absolute: {path}"
        )


class NoFileSpecifiedError(click.UsageError):  # noqa: D101
    def __init__(self) -> None:  # pragma: no cover
        super().__init__("No file specified")


def _add_env_filenames(filenames: tuple[str, ...]) -> tuple[str, ...]:
    """Read additional filenames from BEANCOUNT_FILE."""
    env_filename = os.environ.get("BEANCOUNT_FILE")
    if not env_filename:
        return tuple(dict.fromkeys(filenames))

    env_names = env_filename.split(os.pathsep)
    for name in env_names:
        if not Path(name).is_absolute():
            raise NonAbsolutePathError(name)

    all_names = tuple(env_names) + filenames
    return tuple(dict.fromkeys(all_names))


@click.group(context_settings={"auto_envvar_prefix": "FAVA"})
@click.version_option(version=__version__, prog_name="fava")
def cli() -> None:
    """Fava - web interface for Beancount with PQC security."""
    pass


@cli.command()
@click.argument(
    "filenames",
    nargs=-1,
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
)
@click.option(
    "-p",
    "--port",
    type=int,
    default=5000,
    show_default=True,
    metavar="<port>",
    help="The port to listen on.",
)
@click.option(
    "-H",
    "--host",
    type=str,
    default="localhost",
    show_default=True,
    metavar="<host>",
    help="The host to listen on.",
)
@click.option("--prefix", type=str, help="Set an URL prefix.")
@click.option(
    "--incognito",
    is_flag=True,
    help="Run in incognito mode and obscure all numbers.",
)
@click.option(
    "--read-only",
    is_flag=True,
    help="Run in read-only mode, disable any change through Fava.",
)
@click.option("-d", "--debug", is_flag=True, help="Turn on debugging.")
@click.option(
    "--profile",
    is_flag=True,
    help="Turn on profiling. Implies --debug.",
)
@click.option(
    "--profile-dir",
    type=click.Path(),
    help="Output directory for profiling data.",
)
@click.option(
    "--poll-watcher", is_flag=True, help="Use old polling-based watcher."
)
def start(  # noqa: PLR0913
    *,
    filenames: tuple[str, ...] = (),
    port: int = 5000,
    host: str = "localhost",
    prefix: str | None = None,
    incognito: bool = False,
    read_only: bool = False,
    debug: bool = False,
    profile: bool = False,
    profile_dir: str | None = None,
    poll_watcher: bool = False,
) -> None:  # pragma: no cover
    """Start Fava for FILENAMES on http://<host>:<port>.

    If the `BEANCOUNT_FILE` environment variable is set, Fava will use the
    files (delimited by ';' on Windows and ':' on POSIX) given there in
    addition to FILENAMES.

    Note you can also specify command-line options via environment variables
    with the `FAVA_` prefix. For example, `--host=0.0.0.0` is equivalent to
    setting the environment variable `FAVA_HOST=0.0.0.0`.
    """
    all_filenames = _add_env_filenames(filenames)

    if not all_filenames:
        raise NoFileSpecifiedError

    app = create_app(
        all_filenames,
        incognito=incognito,
        read_only=read_only,
        poll_watcher=poll_watcher,
    )

    if prefix:
        app.wsgi_app = DispatcherMiddleware(  # type: ignore[method-assign]
            simple_wsgi,
            {prefix: app.wsgi_app},
        )

    # ensure that cheroot does not use IP6 for localhost
    host = "127.0.0.1" if host == "localhost" else host
    # Debug mode if profiling is active
    debug = debug or profile

    click.secho(f"Starting Fava on http://{host}:{port}", fg="green")
    if not debug:
        server = Server((host, port), app)
        try:
            server.start()
        except KeyboardInterrupt:
            click.echo("Keyboard interrupt received: stopping Fava", err=True)
            server.stop()
        except OSError as error:
            if "No socket could be created" in str(error):
                raise AddressInUse(port) from error
            raise click.Abort from error
    else:
        setup_debug_logging()
        if profile:
            app.wsgi_app = ProfilerMiddleware(  # type: ignore[method-assign]
                app.wsgi_app,
                restrictions=(30,),
                profile_dir=profile_dir or None,
            )

        app.jinja_env.auto_reload = True
        try:
            app.run(host, port, debug)
        except OSError as error:
            if error.errno == errno.EADDRINUSE:
                raise AddressInUse(port) from error
            raise


# PQC Key Management Commands
@cli.group()
def pqc() -> None:
    """PQC (Post-Quantum Cryptography) key management commands."""
    pass


@pqc.command()
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to crypto settings configuration file.",
)
@click.option(
    "--key-source",
    type=click.Choice(["environment", "file", "vault", "hsm"]),
    default="environment",
    help="Key source type.",
)
def generate(config: str | None, key_source: str) -> None:
    """Generate new PQC keypair."""
    try:
        from fava.pqc.global_config import GlobalConfig
        from fava.pqc.key_manager import PQCKeyManager
        
        # Load configuration
        crypto_settings = GlobalConfig.get_crypto_settings(config)
        
        # Override key source if specified
        if key_source != "environment":
            crypto_settings["wasm_module_integrity"]["key_source"] = key_source
        
        # Initialize key manager
        key_manager = PQCKeyManager(crypto_settings)
        
        click.echo("Generating new PQC keypair...")
        public_key, private_key = key_manager.generate_keypair()
        
        click.echo("Storing keypair...")
        key_manager.store_keypair(public_key, private_key)
        
        click.secho("✓ PQC keypair generated and stored successfully!", fg="green")
        
        # Display key info
        key_info = key_manager.get_key_info()
        click.echo(f"Algorithm: {key_info['algorithm']}")
        click.echo(f"Key Source: {key_info['key_source']}")
        click.echo(f"Public Key Size: {key_info['public_key_size']} bytes")
        click.echo(f"Private Key Size: {key_info['private_key_size']} bytes")
        click.echo(f"Public Key Hash: {key_info['public_key_hash']}")
        
    except Exception as e:
        click.secho(f"✗ Failed to generate keypair: {e}", fg="red", err=True)
        sys.exit(1)


@pqc.command()
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to crypto settings configuration file.",
)
def validate(config: str | None) -> None:
    """Validate current PQC keys."""
    try:
        from fava.pqc.global_config import GlobalConfig
        
        click.echo("Validating PQC keys...")
        
        is_valid = GlobalConfig.validate_key_configuration()
        
        if is_valid:
            click.secho("✓ PQC keys are valid and functional!", fg="green")
            
            # Display key info
            key_info = GlobalConfig.get_key_info()
            click.echo(f"Algorithm: {key_info['algorithm']}")
            click.echo(f"Key Source: {key_info['key_source']}")
            click.echo(f"Status: {key_info['status']}")
            click.echo(f"Public Key Hash: {key_info.get('public_key_hash', 'N/A')}")
        else:
            click.secho("✗ PQC keys validation failed!", fg="red")
            sys.exit(1)
            
    except Exception as e:
        click.secho(f"✗ Key validation error: {e}", fg="red", err=True)
        sys.exit(1)


@pqc.command()
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to crypto settings configuration file.",
)
def info(config: str | None) -> None:
    """Display information about current PQC keys."""
    try:
        from fava.pqc.global_config import GlobalConfig
        
        key_info = GlobalConfig.get_key_info()
        
        click.echo("=== PQC Key Information ===")
        click.echo(f"Algorithm: {key_info.get('algorithm', 'Unknown')}")
        click.echo(f"Key Source: {key_info.get('key_source', 'Unknown')}")
        click.echo(f"Status: {key_info.get('status', 'Unknown')}")
        
        if key_info.get('status') == 'valid':
            click.echo(f"Public Key Size: {key_info.get('public_key_size', 'N/A')} bytes")
            click.echo(f"Private Key Size: {key_info.get('private_key_size', 'N/A')} bytes")
            click.echo(f"Public Key Hash: {key_info.get('public_key_hash', 'N/A')}")
            
            if key_info.get('rotation_enabled'):
                click.echo(f"Key Rotation: Enabled (every {key_info.get('rotation_interval_days', 'N/A')} days)")
                click.echo(f"Last Rotation: {key_info.get('last_rotation', 'Never')}")
                click.echo(f"Next Rotation: {key_info.get('next_rotation', 'N/A')}")
            else:
                click.echo("Key Rotation: Disabled")
        
        if key_info.get('status') == 'error':
            click.secho(f"Error: {key_info.get('error', 'Unknown error')}", fg="red")
        
        click.echo(f"Timestamp: {key_info.get('timestamp', 'N/A')}")
        
    except Exception as e:
        click.secho(f"✗ Failed to get key info: {e}", fg="red", err=True)
        sys.exit(1)


@pqc.command()
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to crypto settings configuration file.",
)
@click.confirmation_option(
    prompt="Are you sure you want to rotate the PQC keys? This will generate new keys and backup the old ones."
)
def rotate(config: str | None) -> None:
    """Rotate PQC keys by generating new ones."""
    try:
        from fava.pqc.global_config import GlobalConfig
        
        click.echo("Starting PQC key rotation...")
        
        success = GlobalConfig.rotate_keys()
        
        if success:
            click.secho("✓ PQC keys rotated successfully!", fg="green")
            
            # Display new key info
            key_info = GlobalConfig.get_key_info()
            click.echo(f"New Public Key Hash: {key_info.get('public_key_hash', 'N/A')}")
            click.echo(f"Rotation Timestamp: {key_info.get('timestamp', 'N/A')}")
        else:
            click.secho("✗ PQC key rotation failed!", fg="red")
            sys.exit(1)
            
    except Exception as e:
        click.secho(f"✗ Key rotation error: {e}", fg="red", err=True)
        sys.exit(1)


@pqc.command()
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to crypto settings configuration file.",
)
def ensure(config: str | None) -> None:
    """Ensure PQC keys exist, generating them if necessary."""
    try:
        from fava.pqc.global_config import GlobalConfig
        
        click.echo("Ensuring PQC keys exist...")
        
        success = GlobalConfig.ensure_keys_exist()
        
        if success:
            click.secho("✓ PQC keys are available!", fg="green")
            
            # Display key info
            key_info = GlobalConfig.get_key_info()
            click.echo(f"Algorithm: {key_info['algorithm']}")
            click.echo(f"Key Source: {key_info['key_source']}")
            click.echo(f"Public Key Hash: {key_info.get('public_key_hash', 'N/A')}")
        else:
            click.secho("✗ Failed to ensure PQC keys exist!", fg="red")
            sys.exit(1)
            
    except Exception as e:
        click.secho(f"✗ Key initialization error: {e}", fg="red", err=True)
        sys.exit(1)


# Maintain backward compatibility for the original main function
def main() -> None:  # pragma: no cover
    """Entry point for backward compatibility."""
    cli()


# needed for pyinstaller:
if __name__ == "__main__":  # pragma: no cover
    cli()