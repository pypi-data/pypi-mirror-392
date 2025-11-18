# Contributing

📜 _Package is currently developed with an open-source philosophy, so any relevant contribution is welcome_

## General rules

In an ideal world, your code should be :

- _**simple** enough so your grandma can understand it_
- _**beautiful** enough to make your cousin in art school want to read it_
- _**efficient** enough such that you spend more time analyzing your plots than coding and running experiments_

Of course, that's an ideal goal ... but nothing prevents to aim at the sky when reaching the top of the mountain 🚡

Recommended approach is to **fork this repository**, create a new branch in your fork named with the reason of your PR
(don't use `main` !), and open a **pull request** when ready.
This will automatically trigger the CI pipeline that :

1. check linting with `flake8`
2. run all the tests defined in the [`tests` folder](https://github.com/CompMath-TUHH/MaRGE_3D_solver/tree/main/tests), and upload a coverage report to [`codecov`](https://app.codecov.io/gh/CompMath-TUHH/MaRGE_3D_solver)
3. test all the tutorials located in the [`docs/notebook` folder](https://github.com/CompMath-TUHH/MaRGE_3D_solver/tree/main/docs/notebooks)

Recommended merge strategy is to squash commits $\Rightarrow$ you don't have to care about the number of commit included in your PR, so don't be scare of making mistakes before your PR is accepted 😉

> 🔔 Once your PR is accepted, please delete the development branch from your fork and synchronize your `main` branch. When creating a new development branch later, ensure that you start from an up-to-date `main` branch of your fork.

## Base recipes

_Some memos on how to develop this package ..._

- [Testing your changes](./devdoc/testing.md)
- [Update this documentation](./devdoc/updateDoc.md)
- [Version update pipeline](./devdoc/versionUpdate.md)

```{eval-rst}
.. toctree::
    :maxdepth: 1
    :hidden:

    devdoc/testing
    devdoc/updateDoc
    devdoc/versionUpdate
```