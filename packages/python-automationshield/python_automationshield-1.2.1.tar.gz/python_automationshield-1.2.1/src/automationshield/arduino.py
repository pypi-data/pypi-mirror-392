"""This module provides several functions to download the `arduino-cli`_ and install firmware on an Arduino board.

.. _arduino-cli: https://arduino.github.io/arduino-cli/
"""

import platform
import subprocess
import sys

from math import log
from pathlib import Path
from shutil import unpack_archive
from typing import Optional
from urllib.request import urlretrieve


LEONARDO: str = "arduino:avr:leonardo"
"""FQBN for Arduino Leonardo."""

UNO: str = "arduino:avr:uno"
"""FQBN for Arduino UNO."""

MEGA: str = "arduino:avr:mega"
"""FQBN for Arduino MEGA and MEGA 2560."""

src_dir: Path = Path(__file__).parent
"""Path to the automationshield src directory on the system.

:meta hide-value:
"""

script_dir: Path = src_dir / "arduino"
"""Path to the directory containing the Arduino script directories.

:meta hide-value:
"""

out_dir: Path = script_dir / "out"
"""Path to the directory containing the .hex files.

:meta hide-value:
"""

cli_dir: Path = script_dir / "arduino-cli"
"""Path to the directory containing the ``arduino-cli``.

:meta hide-value:
"""

cli_path: Path = cli_dir / "arduino-cli"
"""Path to the ``arduino-cli`` executable.

:meta hide-value:
"""


def download_cli(system:str):
    """Download the ``arduino-cli`` for the appropriate system. The executable is placed in :py:const:`cli_dir`.

    :param system: Name of operating system. Result of calling :py:meth:`platform.system`.
    """
    base_url = "https://downloads.arduino.cc/arduino-cli/"
    system_bits = int(log(sys.maxsize + 1, 2) + 1)

    if system == "Windows":
        url = base_url + f"arduino-cli_latest_Windows_{system_bits}bit.zip"
        zip_name = "arduino-cli.zip"

    elif system == "Linux":
        if "ARM" in platform.machine().upper():

            if system_bits == 64:
                url = base_url + f"arduino-cli_latest_Linux_ARM64.tar.gz"
            else:
                url = base_url + f"arduino-cli_latest_Linux_ARMv7.tar.gz"

        else:
            url = base_url + f"arduino-cli_latest_Linux_{system_bits}bit.tar.gz"

        zip_name = "arduino-cli.tar.gz"

    elif system == "Darwin":
        url = base_url + f"arduino-cli_latest_macOS_64bit.tar.gz"
        zip_name = "arduino-cli.tar.gz"

    zip_path = src_dir / zip_name
    urlretrieve(url, zip_path)
    unpack_archive(zip_path, cli_dir)
    zip_path.unlink()


def setup_cli():
    """Run setup for ``arduino-cli``. This function calls the following methods of the ``arduino-cli``:

    .. code-block:: console
        :linenos:

        arduino-cli core update-index
        arduino-cli core install arduino:avr

    These respectively update the index of cores to the latest version and downloads the core for AVR boards, which includes a.o. the Arduino UNO, Mega (2560) and Leonardo.
    """
    # update index
    subprocess.run(
        [cli_path, "core", "update-index"]
    )

    # install core for AVR boards (includes Leonardo, UNO, Mega)
    subprocess.run(
        [cli_path, "core", "install", "arduino:avr"]
    )


def compile_script(device:str, script:str):
    """Compile an Arduino script for a specific Arduino board and Automationshield.

    .. code-block:: console
        :linenos:

        arduino-cli compile
            --fqbn {device}
            --clean
            --libraries {arduino.script_dir}/lib
            --export-binaries
            {arduino.script_dir}/{script}

    :param device: FQBN of Arduino board.
    :param script: Directory name of the Arduino code to be installed. Script directory are provided as a property of the shield classes, e.g.: :py:attr:`automationshield.AeroShield.script`.
    """
    result = subprocess.run(
        [cli_path, "compile",
         "--fqbn", device,
         "--clean",
         "--libraries", script_dir / "lib",
         "--export-binaries",
         script_dir / script]
    )
    result.check_returncode()


def upload_script(device:str, script:str, port:str, hex:Optional[str]=None):
    """Upload compiled script onto Arduino board.

    .. code-block:: console
        :linenos:

        arduino-cli upload
            --input-file {file}
            --fqbn {device}
            --port {port}
            {arduino.script_dir}/{script}

    In the command, the `file` argument points to the appropriate ``.hex`` file in :py:const:`arduino.out_dir`. This can be overridden by providing the ``hex`` argument.

    :param device: FQBN of Arduino board.
    :param script: Directory name of the Arduino code to be installed. Script directory are provided as a property of the shield classes, e.g.: :py:attr:`automationshield.AeroShield.script`.
    :param port: Port where the Arduino board is connected. Shield classes provide a :py:attr:`port` attribute that can be used.
    :param hex: ``.hex`` file to upload. Optional, defaults to the appropriate file in :py:const:`~automationshield.arduino.out_dir`.
    """
    result = subprocess.run(
        [cli_path, "upload",
         "--input-file", (out_dir / f"{script}.ino.hex") if hex is None else hex,
         "--fqbn", device,
         "--port", port,
         script_dir / script]
    )
    result.check_returncode()
