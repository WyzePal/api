# WyzePal API

![Build status](https://travis-ci.org/wyzepal/python-wyzepal-api.svg?branch=master)
[![Coverage status](https://img.shields.io/codecov/c/github/wyzepal/python-wyzepal-api/master.svg)](
https://codecov.io/gh/wyzepal/python-wyzepal-api)

This repository contains the source code for WyzePal's PyPI packages:

* `wyzepal`: [PyPI package](https://pypi.python.org/pypi/wyzepal/)
  for WyzePal's API bindings.
* `wyzepal_bots`: [PyPI package](https://pypi.python.org/pypi/wyzepal-bots)
  for WyzePal's bots and bots API.
* `wyzepal_botserver`: [PyPI package](https://pypi.python.org/pypi/wyzepal-botserver)
  for WyzePal's Flask Botserver.

The source code is written in *Python 3*.

## Development

This is part of the WyzePal open source project; see the
[contributing guide](https://wyzepal.readthedocs.io/en/latest/overview/contributing.html)
and [commit guidelines](https://wyzepal.readthedocs.io/en/latest/contributing/version-control.html).

1. Fork and clone the Git repo:
   `git clone https://github.com/<your_username>/python-wyzepal-api.git`

2. Make sure you have [pip](https://pip.pypa.io/en/stable/installing/)
   and [virtualenv](https://virtualenv.pypa.io/en/stable/installation/)
   installed.

3. `cd` into the repository cloned earlier:
   `cd python-wyzepal-api`

4. Run:
   ```
   python3 ./tools/provision
   ```
   This sets up a virtual Python environment in `wyzepal-api-py<your_python_version>-venv`,
   where `<your_python_version>` is your default version of Python. If you would like to specify
   a different Python version, run
   ```
   python3 ./tools/provision -p <path_to_your_python_version>
   ```

5. If that succeeds, it will end with printing the following command:
   ```
   source /.../python-wyzepal-api/.../activate
   ```
   You can run this command to enter the virtual environment.
   You'll want to run this in each new shell before running commands from `python-wyzepal-api`.

6. Once you've entered the virtualenv, you should see something like this on the terminal:
   ```
   (wyzepal-api-py3-venv) user@pc ~/python-wyzepal-api $
   ```
   You should now be able to run any commands/tests/etc. in this
   virtual environment.

### Running tests

To run the tests for

* *wyzepal*: run `./tools/test-wyzepal`

* *wyzepal_bots*: run `./tools/test-lib && ./tools/test-bots`

* *wyzepal_botserver*: run `./tools/test-botserver`

To run the linter, type:

`./tools/lint`

To check the type annotations, run:

`./tools/run-mypy`
