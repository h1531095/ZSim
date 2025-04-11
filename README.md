# ZZZ_Calculator

English | [文档](README_CN.md)

**Introduction**

`ZZZ_Calculator` is a web-based damage calculator for Zenless Zone Zero. It provides a user-friendly interface to calculate the total damage output of a team composition, taking into account the characteristics of each character's weapon and equipments. Then, it simulates a combo sequence you entered to estimate the damage output.

## Features

- Calculate total damage based on team composition
- Incorporates weapon and skill characteristics of each character
- Simulates a combo sequence to estimate damage output
- Draw a line chart to show the damage distribution
- Provides detailed damage information for each character
- Developing~

## Usage

Clone the repository to your local directory.

```
$ git clone https://github.com/Steinwaysj/ZZZ_Calculator.git
```

Install the dependencies. Project is compatible with Python 3.12 or later.

```
$ pip install -r requirements.txt
```

Then run the webui.

```
$ run
```

CLI version is also available (yet at least).

```
$ python main.py
```

*Experimental:*

*If you want to compile the C/C++ Extension Module, you can use the following command.
Make sure you have a C compiler installed.*

```
$ python setup.py build_ext --inplace
```

## TODO LIST

Go check issues for more details.
