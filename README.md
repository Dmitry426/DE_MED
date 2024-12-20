# Data Engineering Med Project



#### Python Runner

```bash
python3 run_service.py
```

#### Project Build 

```bash
make build
```

### Run entrypoint from console 

```bash
 poetry medical-data-processor
```

#### Project linting:

```bash
make lint
```

### Before You Begin


```bash
make dev
```

This command to set up pre commit config in order to check your code before commit 

### Dependency's

Dependency management is handled by the poetry utility. 
The list of dependencies is in the pyproject.toml file. 
Instructions for setting up a poetry environment for PyCharm can be found here.
To add a dependency, simply write poetry add requests,
and the utility will automatically choose a version that does not conflict with current dependencies. 
Dependencies with exact versions are recorded in the poetry.lock file. To get a dependency tree, you can use the command poetry show --tree. 
Other commands are available in the official documentation for the utility.



