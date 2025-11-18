from typing import overload

def _run_cli(args: list[str]) -> bool:
    """
    Run the Syside license checker CLI.
    """

@overload
def check() -> None:
    """
    Check the validity of the license stored in the environment variable
    `SYSIDE_LICENSE_KEY`.

    :raises RuntimeError: If validity check fails.
    """

@overload
def check(
    license_key: str | None = None,
    renew_if_shorter: int = 3 * 60 * 60,
    renew_duration: int = 7 * 24 * 60 * 60,
    license_key_file: str | None = None,
    silent: bool = True,
) -> None:
    """
    Check the validity of the license and ensure that the Automator license file
    is valid for at least the given duration.

    :param license_key: The Syside license key. If not provided, the license key
        will be obtained from the environment variable `SYSIDE_LICENSE_KEY`.
    :param renew_if_shorter: The duration in seconds (default: 3 hours). If the
        license file is valid for shorter time than this duration, it will be
        renewed.
    :param renew_duration: The duration in seconds (default: 1 week). If the
        license file is valid for shorter time than this duration, it will be
        renewed.
    :param license_key_file: The path to the file containing the license key.
    :param silent: Whether to suppress the output.
    :raises OverflowError: If `renew_if_shorter` or `renew_duration` is negative.
    :raises RuntimeError: If validity check fails.
    """

def _get_default_primary_license_file_path() -> str:
    """
    Get the default primary location for the Syside license file.
    """

def _get_default_secondary_license_file_path() -> str | None:
    """
    Get the default secondary location for the Syside license file.
    """

def _get_default_license_file_name() -> str:
    """
    Get the default name for the Syside license file.
    """
