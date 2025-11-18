# Testing your changes

📜 _After doing some changes / corrections / addition in the code, you can run all the CI tests locally before any commit or PR._

## Install test dependencies

For reproducibility, it is recommended to use a dedicated environment to install all dependencies.
You can do that by running from `marge3d` root folder :

```bash
python -m venv env
```

$\Rightarrow$ this will create a `env` folder in the root folder (ignored by `git`),
that you can activate using :

```bash
source ./env/bin/activate
```

> 🔔 In case you have the `base` `conda` environment as default on your computer,
> you should deactivate it before activating `env` by running `conda deactivate`.

If not already done, install all the test dependencies listed in the [pyproject.toml](../../pyproject.toml) file
under the `project.optional-dependencies` section.
Those can be installed (if not already on your system)
by running from the root folder :

```bash
pip install -e .[test]     # install marge3d locally and all test dependencies
# on MAC-OS : pip install -e ".[test]"
```

> 📣 Remember that this is the [recommended installation approach for developers](../installation).

## Test local changes

Run the full test series with :

```bash
pytest -v ./tests
```

This will run all tests currently implemented for `marge3d`.`

## Check code coverage

You can also check code coverage of all current tests by running (from the root folder) :

```bash
pytest --cov --cov-report=html -v --durations=0 ./tests
```

This generates a html coverage report in `htmlcov/index.html` that you can read using your favorite web browser.

## Testing notebook tutorials

All notebooks are located in the [notebook docs folder](../notebooks). You can first check if they can be executed properly by running :

```bash
cd docs/notebooks
./run-sh --all
```

💡 To execute only one notebook, simply run _e.g_ :

```bash
./run.sh 01_firstSteps.ipynb
```

Finally, you can test all notebooks by running :

```bash
pytest ./ --nb-test-files -v
```

This will re-run each instructions in the notebooks, and compare if the generated outputs are identical to those of the locally stored notebook.