# ZZZ_Calculator

English | [中文](./docs/README_CN.md)

**Introduction**

`ZZZ_Calculator` is a web-based damage calculator for Zenless Zone Zero. It provides a user-friendly interface to calculate the total damage output of a team composition, taking into account the characteristics of each character's weapon and equipments. Based on the preset APL (Action Priority List), it automatically simulates the sequence of character actions in the team, triggers buffs, records and analyzes the results, and generates visual charts.

## Features

- Calculate total damage based on team composition
- Simulate damage output based on APL
- Generate visual charts
- Provide detailed damage information for each character

## Usage

Clone the repository to your local directory.

```bash
git clone https://github.com/Steinwaysj/ZZZ_Calculator.git
```

Install the dependencies. Project is compatible with Python 3.12 or later.

```bash
pip install -r requirements.txt
```

Then run the webui.

```bash
run
```

CLI version is also available (yet at least).

```bash
python main.py
```

*Experimental:*

*If you want to compile the C/C++ Extension Module, you can use the following command.
Make sure you have a C compiler installed.*

```bash
python setup.py build_ext --inplace
```

## TODO LIST

Go check issues for more details.
