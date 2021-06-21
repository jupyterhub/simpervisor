# How to make a release

`simpervisor` is a package [available on
PyPI](https://pypi.org/project/jupyterhub-simpervisor/) and
[conda-forge](https://conda-forge.org/). These are instructions on how to make a
release on PyPI. The PyPI release is done automatically by a GitHub workflow
when a tag is pushed.

For you to follow along according to these instructions, you need:

- To have push rights to the [simpervisor GitHub
  repository](https://github.com/jupyterhub/simpervisor).

## Steps to make a release

1. Update [CHANGELOG.md](CHANGELOG.md). Doing this can be made easier with the
   help of the
   [choldgraf/github-activity](https://github.com/choldgraf/github-activity)
   utility to list merged PRs and generate a list of contributors.

   ```bash
   github-activity jupyterhub/simpervisor --output tmp-changelog-prep.md
   ```

1. Once the changelog is up to date, checkout main and make sure it is up to date and clean.

   ```bash
   ORIGIN=${ORIGIN:-origin} # set to the canonical remote, e.g. 'upstream' if 'origin' is not the official repo
   git checkout main
   git fetch $ORIGIN main
   git reset --hard $ORIGIN/main
   # WARNING! This next command deletes any untracked files in the repo
   git clean -xfd
   ```

1. Set the `version` field in [setup.py](setup.py) appropriately and make a
   commit.

   ```bash
   git add setup.py
   VERSION=...  # e.g. 1.2.3
   git commit -m "release $VERSION"
   ```

1. Reset the `version` field in [setup.py](setup.py) appropriately with an
   incremented patch version and a `dev` element, then make a commit.

   ```bash
   git add setup.py
   git commit -m "back to dev"
   ```

1. Push your two commits to main.

   ```bash
   # first push commits without a tags to ensure the
   # commits comes through, because a tag can otherwise
   # be pushed all alone without company of rejected
   # commits, and we want have our tagged release coupled
   # with a specific commit in main
   git push $ORIGIN main
   ```

1. Create a git tag for the pushed release commit and push it.

   ```bash
   git tag -a $VERSION -m $VERSION HEAD~1

   # then verify you tagged the right commit
   git log

   # then push it
   git push $ORIGIN refs/tags/$VERSION
   ```

1. Push your two commits to main along with the annotated tags referencing
   commits on main. A GitHub Workflow will trigger automatic deployment of the
   pushed tag.

   ```bash
   # pushing the commits standalone allows you to
   # ensure you don't end up only pushing the tag
   # because the commit were rejected but the tag
   # wasn't
   git push $ORIGIN main

   # if you could push the commits without issues
   # go ahead and push the tag also
   git push --follow-tags $ORIGIN main
   ```

1. Verify that [the GitHub
   workflow](https://github.com/jupyterhub/simpervisor/actions?query=workflow%3ARelease)
   triggers and succeeds and that that PyPI received a [new
   release](https://pypi.org/project/simpervisor/).

1. Following the release to PyPI, an automated PR should arrive to
   [conda-forge/simpervisor-feedstock](https://github.com/conda-forge/simpervisor-feedstock),
   check for the tests to succeed on this PR and then merge it to successfully
   update the package for `conda` on the conda-forge channel.
