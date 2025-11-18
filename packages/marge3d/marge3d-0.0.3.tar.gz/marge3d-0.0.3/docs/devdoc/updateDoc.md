# Update this documentation

📜 _If you think it can be clearer, or you want to add more details or tutorials ..._


## Generating local docs

First you need a few dependencies (besides those for `marge3d`).
For that download the [source code](https://github.com/CompMath-TUHH/MaRGE_3D_solver)
and install the package with all the `docs` dependencies locally :

```bash
git clone https://github.com/CompMath-TUHH/MaRGE_3D_solver.git
cd MaRGE_3D_solver
pip install -e .[docs]  # on MAC-OS : pip install -e ".[docs]"
```

> 📜 The `-e` option ensures that your installed python package is directly linked to the sources (no copy of code),
> hence modifying any part of the source code (in particular the documentation)
> will be taken into account when `sphinx` will parse the code docstring.

Then to generate the documentation website locally, simply run :

```bash
cd docs
make html
```

This builds the `sphinx` documentation automatically in a `_build` folder,
and you can view it by opening `docs/_build/html/index.html` using your favorite browser.


## Updating a tutorial

When changing a [notebook tutorial](../notebooks), you should also regenerate it entirely, in particular if you modified parts of the code.
You can do that by running :

```bash
cd notebooks
./run.sh $NOTEBOOK_FILE
```

If you modified several notebooks, and as a safety, it is also possible to regenerate all doing :

```bash
./run.sh --all
```

> 📣 When modifying only the markdown text in a notebooks, it is not necessary to regenerate it.


## Adding a tutorial

Just add a notebook in the [notebook folder](../notebooks) with a name like this :
`{idx}_{shortName}.ipynb` with `idx` a zero-padded index (starts at `01`).
This will be automatically added in the documentation and tested by the [CI pipeline](testing.md#testing-notebook-tutorials).

> 💡 Don't hesitate to look at the other notebooks to use a common and consistent formatting ...