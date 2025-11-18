from .controller import ShieldController
from .exception import AutomationShieldException
from .shields import AeroShield, AeroShieldMimic, FloatShield, MagnetoShield, StateSpaceShield


# install arduino-cli if not present
import platform

from .arduino import download_cli, setup_cli, cli_dir

system = platform.system()

if system in ("Windows", "Linux", "Darwin"):
    if not cli_dir.exists():
        print(f"Downloading arduino-cli to {cli_dir}")
        download_cli(system)
        print("Performing setup for arduino-cli")
        setup_cli()

    else:
        print(f"Arduino-cli found in {cli_dir}")

else:
    print("Arduino-cli not available for current machine")
