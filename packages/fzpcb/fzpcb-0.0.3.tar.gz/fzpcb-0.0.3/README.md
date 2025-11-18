# fzpcb

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install fzpcb
```
## Usage

```console
fzpcb INPUT-YAML 
```
## YAML Example

This is an example YAML file for a DRV8833 breakout board:

```console
metadata:
    author: Phil Tregoning
    version: 1
    title: DollaTek DRV8833
    label: DRV8833
    description: DollaTek DRV8833 1.5A 2-Channel DC Motor Driver Board
tags:
    - DollaTek
    - DRV8833
    - motor-driver
    - stepper-motor-driver
properties:
    family: motor-driver
    voltage: 3 to 10V
    chip: DRV8833
layout:
    - '01KF..Wf+.cF12'
    - '02.kM++++...11'
    - '03.######.cF10'
    - '04.======...09'
    - '05..T1..kf..08'
    - '06.Ef+......07'
connectors:
    1: EEP Protection output
    2: OUT1 H bridge 1 output 1
    3: OUT2 H bridge 1 output 2
    4: OUT3 H bridge 2 output 1
    5: OUT4 H bridge 2 output 2
    6: ULT Ulta-low sleep mode
    12: IN4 H bridge 2 input 2
    11: IN3 H bridge 2 input 1
    10: GND Ground
    9: VCC Voltage in 3 to 10V
    8: IN2 H bridge 1 input 2
    7: IN1 H bridge 1 input 1
text:
    T1: DRV8833
```

## License

`fzpcb` is distributed under the terms of the [GPL-3.0-only](https://spdx.org/licenses/GPL-3.0-only.html) license.
