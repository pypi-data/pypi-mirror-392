# fastinit

A simple CLI to quickly and cleanly create FastAPI projects and modules.

> This package provides commands to generate the basic structure of a FastAPI project, along with scaffolding for modules including routes, schemas, models, and services.

## Installation

~~~~bash
pip install fastinit
~~~~
## Usage
After installing the package, you will have access to the `fastinit` command in your terminal, which displays the available commands:

~~~~plaintext
#root@machine:~# fastinit
  __           _   _       _ _   
 / _| __ _ ___| |_(_)_ __ (_) |_
| |_ / _` / __| __| | '_ \| | __|
|  _| (_| \__ \ |_| | | | | | |_
|_|  \__,_|___/\__|_|_| |_|_|\__|


                         by jp066

- Use 'fastinit new <project_name>' to create a new FastAPI project.
- Use 'fastinit g module <project_name> <module_name>' to create a new module.
~~~~

Create a new FastAPI project:
~~~~
fastinit new project_name
~~~~
Generate a complete module:
~~~~
fastinit g module module_name
~~~~

### Requirements
- Python 3.8+
- FastAPI (to use the generated project)


### Contributing
Pull requests are welcome.
---

Made by João Pedro.