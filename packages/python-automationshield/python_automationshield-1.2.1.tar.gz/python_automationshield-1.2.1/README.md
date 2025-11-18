# python-automationshield

`python-automationshield` is a Python package that implements a Python interface to [Automationshield](https://github.com/gergelytakacs/AutomationShield)'s devices. Automationshield creates cheap and accessible tools for control engineering education in the form of Arduino shields. Much of the Arduino code used in this package is derived from the code in the [Automationshield](https://github.com/gergelytakacs/AutomationShield) repository.

Currently, this package has Python implementations for the following shields:

- [Aeroshield](https://github.com/gergelytakacs/AutomationShield/wiki/AeroShield)
- [Floatshield](https://github.com/gergelytakacs/AutomationShield/wiki/FloatShield)
- [Magnetoshield](https://github.com/gergelytakacs/AutomationShield/wiki/MagnetoShield)

In addition, this package contains simulator for the implemented shields which allow to run run experiments and test controllers without a physical device. A simulator is available for the following shields:

- AeroShield: `AeroShieldMimic`

This project was built to allow TU Delft students learning control engineering to use Python in their assignments, since that is what they are thought in the curriculum. This package provides a flexible controller class that lets users conveniently implement a controller and test it on the hardware without having to reupload new firmware to the Arduino board.

This project was developed using [Arduino Leonardo](https://docs.arduino.cc/hardware/leonardo/) boards. The code may work on other devices as well, but it will likely need a few changes. You are welcome to submit a pull request to add functionality for additional Arduino boards!

## Installation

`python-automationshield` requires Python >= 3.10 and can be installed with the following command:

```bash
$ pip install python-automationshield
```

## Usage

<!-- - TODO: basic basic example, live plot visuals. link to examples -->
Below is a very simple example with the AeroShield to get started. Read more in the [documentation](https://python-automationshield.readthedocs.io).

### Install the firmware on an Arduino board

When first importing the module, `AutomationShield` will download the [`arduino-cli`](https://arduino.github.io/arduino-cli/) to the package directory. The `arduino-cli` is used to flash the correct firmware onto your Arduino board. The package _should_ download the correct executable for your operating system and architecture, but it has only been tested on a 64-bit Windows system.

```python
from automationshield import AeroShield
from automationshield.arduino import UNO  # import the FQBN for the UNO from the arduino module

aero_shield = AeroShield()
aero_shield.install_firmware(device=UNO)

#optionally check that the correct firmware is installed
with aero_shield:
    print(aero_shield.check_firmware)  # this will print the version number of the Arduino code if the firmware is correct and throw an exception otherwise.
```

### Send commands to the `AeroShield` and read its state

```python
from automationshield import AeroShield


with AeroShield() as aero_shield:
    for _ in range(100):
        aero_shield.write(flag=aero_shield.RUN, motor=50)
        out = aero_shield.read()
        print(f"Potentiomneter [%]: {out[0]}, Angle [°]: {out[1]}")
```

### Use the `ShieldController` class to conveniently implement a controller

```python
from automationshield import AeroShield, ShieldController


class MyController(ShieldController):
    def controller(self, t: float, dt: float, ref: float, pot: float, angle: float) -> float:
        """Set the motor value to the provided reference."""
        return ref


shield = AeroShield()
# create controller instance
my_controller = MyController(shield)
# run the controller on the Arduino.
hist = my_controller.run(freq=200, cycles=1000, ref=45)
```

### Plot the experiment data using the `plotting.Plotter` class

```python
from automationshield.plotting import Plotter


fig, ax = Plotter(shield).plot(hist)
fig.show()
```

Below is an example of a figure plotting the result of a PID controller on the AeroShield with a constant reference at 45°.

![Plot of PID controller output](https://gitlab.com/mrtreasurer/python-automationshield/-/raw/main/docs/images/pid_controller_output.png)

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`python-automationshield` was created by Bert Van den Abbeele. It is licensed under the terms of the MIT license.

## Credits

`python-automationshield` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
