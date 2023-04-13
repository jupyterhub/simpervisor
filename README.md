# simpervisor

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/jupyterhub/simpervisor/test.yaml?branch=main&logo=github&label=tests)](https://github.com/jupyterhub/simpervisor/actions)
[![Codecov](https://img.shields.io/codecov/c/github/jupyterhub/simpervisor?logo=codecov&logoColor=white)](https://codecov.io/gh/jupyterhub/simpervisor)
[![Latest PyPI version](https://img.shields.io/pypi/v/simpervisor?logo=pypi)](https://pypi.python.org/pypi/simpervisor)
[![Latest conda-forge version](https://img.shields.io/conda/vn/conda-forge/simpervisor?logo=conda-forge)](https://anaconda.org/conda-forge/simpervisor)
[![GitHub](https://img.shields.io/badge/issue_tracking-github-blue?logo=github)](https://github.com/jupyterhub/simpervisor/issues)
[![Discourse](https://img.shields.io/badge/help_forum-discourse-blue?logo=discourse)](https://discourse.jupyter.org/c/jupyterhub)
[![Gitter](https://img.shields.io/badge/social_chat-gitter-blue?logo=gitter)](https://gitter.im/jupyterhub/jupyterhub)

simpervisor provides the SupervisedProcess class that provides async methods
`start`, `ready`, `terminate`, and `kill` to manage it. As an example of how it
can be used, see [how jupyterhub/jupyter-server-proxy uses it][].

[how jupyterhub/jupyter-server-proxy uses it]: https://github.com/jupyterhub/jupyter-server-proxy/blob/969850eb0be2f8d016974104497109e0d13ddc94/jupyter_server_proxy/handlers.py#L650-L660
