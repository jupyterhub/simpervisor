# How to make a release

`simpervisor` is a package available on [PyPI] and [conda-forge].
These are instructions on how to make a release.

## Pre-requisites

- Push rights to [github.com/jupyterhub/simpervisor]

## Steps to make a release

1. Create a PR updating `CHANGELOG.md` with [github-activity] and continue
   only when its merged.

1. Checkout main and make sure it is up to date.

   ```shell
   git checkout main
   git fetch origin main
   git reset --hard origin/main
   ```

1. Update the version, make commits, and push a git tag with `tbump`.

   ```shell
   pip install tbump
   tbump --dry-run ${VERSION}

   # run
   tbump ${VERSION}
   ```

   Following this, the [CI system] will build and publishe a release.

1. Reset the version back to dev, e.g. `1.0.1.dev` after releasing `1.0.0`.

   ```shell
   tbump --no-tag ${NEXT_VERSION}.dev
   ```

1. Following the release to PyPI, an automated PR should arrive within 24 hours
   to [conda-forge/simpervisor-feedstock] with instructions on releasing to
   conda-forge. You are welcome to volunteer doing this, but aren't required as
   part of making this release to PyPI.

[github-activity]: https://github.com/executablebooks/github-activity
[github.com/jupyterhub/simpervisor]: https://github.com/jupyterhub/simpervisor
[pypi]: https://pypi.org/project/simpervisor/
[conda-forge]: https://anaconda.org/conda-forge/simpervisor
[conda-forge/simpervisor-feedstock]: https://github.com/conda-forge/simpervisor-feedstock
[ci system]: https://github.com/jupyterhub/simpervisor/actions/workflows/release.yaml
