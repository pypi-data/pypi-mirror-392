# Version update pipeline

## Release conventions

For each version update (_a.k.a_ releases), we use the following denomination :

- patch : from `*.*.{i}` to `*.*.{i+1}` $\Rightarrow$ minor modifications, bugfixes, code reformating, additional aliases for generators
- minor : from `*.{i}.*` to `*.{i+1}.0` $\Rightarrow$ addition of new features, utility functions, scripts, ...
- major : from `{i}.*.*` to `{i+1}.0.0` $\Rightarrow$ major changes in code structure, design and API

Here are some generic recommendation on release-triggering events :

1. patch version should be released every three months in case some only patch-type changes have been done
2. minor version should be released after merging a PR including new features (requires a version dump commit, see below ...)
3. major version are released when important changes have been done on a development branch named `v{i+1}-dev` hosted on the main repo. Requires a full update of the documentation and code, maybe with some migration guide, etc ... Before merging `v{i+1}-dev` into `main`, a `v{i}-lts` branch can be created from it to keep track of the old version.

## Pipeline description

To release a new version, one need maintainer access to the `marge3d` Github project, and execute the following steps :

1. Modify the **version number** in [`pyproject.toml`](https://github.com/CompMath-TUHH/MaRGE_3D_solver/blob/main/pyproject.toml)
2. Modify the **version number and release date** in [`CITATION.cff`](https://github.com/CompMath-TUHH/MaRGE_3D_solver/blob/main/CITATION.cff)
3. Commit with message `XX: bump version to x.x.x` where `XX` are your initials and `x.x.x` is the new version
4. Manually run the ["Publish to PyPI 📦"](https://github.com/CompMath-TUHH/MaRGE_3D_solver/actions/workflows/publish.yml) workflow
5. [Draft a new release](https://github.com/CompMath-TUHH/MaRGE_3D_solver/releases/new) associated to a new tag `v*.*.*` (with `*.*.*` the new version, and the `+ Create new tag: ... on publish` button)
6. Find a cool title for the release, and describe what is new or changed (don't forget to thanks the non-maintainers authors)

And finally, click on `Publish release` 🚀
