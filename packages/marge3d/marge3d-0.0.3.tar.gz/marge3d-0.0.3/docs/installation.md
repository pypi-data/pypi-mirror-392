
# Installation

## Using PyPI

You can download the latest version from [`pypi`](https://pypi.org) using `pip` :

```bash
pip install marge3d
```

## Using conda

Currently, no version is distributed on conda-forge. However using `pip` from `conda` will install `marge3d` in your conda environment.

If you are using a `environment.yml` file with conda, then you can add it as a dependency like this :

```yaml
name: yourEnv
channels:
  - conda-forge
  - defaults
dependencies:
  ...
  - pip
  - pip:
    - marge3d
```

## Install from source

In case you want the latest revision (or a specific branch), you can directly clone the sources from `github` :

```bash
git clone https://github.com/CompMath-TUHH/MaRGE_3D_solver.git
```

If you **want to use the package only**, simply use the `pip` local installer directly :

```bash
cd MaRGE_3D_solver     # go into the local git repo
pip install .
```

For **developers who want to contribute**, recommended approach is to install
the package in _editable mode_ :

```bash
cd MaRGE_3D_solver       # go into the local git repo (if not already there)
pip install -e .[tests]  # on MAC-OS : pip install -e ".[tests]"
```

This will link your python installation to your local `marge3d` folder,
hence all your modifications will be taken into account at each new import of `marge3d`.

> 🔔 Some IDEs also modify the `PYTHONPATH` to include the `marge3d` root folder, which you can also do manually if you prefer.
