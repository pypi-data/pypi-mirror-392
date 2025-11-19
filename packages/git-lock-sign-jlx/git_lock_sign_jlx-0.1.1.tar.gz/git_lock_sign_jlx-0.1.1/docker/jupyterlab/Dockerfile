ARG BASE_CONTAINER=polusai/notebook:2.1.3
FROM $BASE_CONTAINER

LABEL hash=generated

# Fix: https://github.com/hadolint/hadolint/wiki/DL4006
# Fix: https://github.com/koalaman/shellcheck/wiki/SC3014
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Environment variables (early setup)
ENV XDG_CACHE_HOME="/home/$NB_USER/.cache/" \
    PS1="\u $ "
USER root

# Install apt packages first (these rarely change)
RUN apt-fast update && \
    apt-fast install -yq --no-install-recommends fonts-liberation pandoc run-one curl git tzdata unzip openssh-client less texlive-xetex texlive-fonts-recommended texlive-plain-generic xclip emacs inkscape libsm6 libxext-dev libxrender1 lmodern ffmpeg ssh procps libicu-dev rsync screen  && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER $NB_UID
WORKDIR /tmp

# Install conda packages (expensive operation, cache-friendly)
RUN mamba install --yes \
jupyter_core notebook=7.3.2 nbclassic=1.1.0 jupyter_server=2.15.0 jupyterlab=4.3.5 jupyterhub=5.1.0 jupyterlab-git=0.50.1 jupyterlab-latex=4.1.4 jupyterlab-myst=2.4.2 jupyter-archive=3.4.0 jupyter-ai=2.22.0 jupyter-resource-usage=1.1.0 jupyterlab-tour=4.0.1 jupyterlab-lsp=5.1.0 python-lsp-server=1.11.0 papermill=2.6.0 numexpr=2.10.0 matplotlib-base=3.9.2 scipy=1.14.0 feather-format=0.4.1 nbformat=5.10.4 sos-notebook=0.24.4 jupyterlab-sos=0.10.4 sos-papermill=0.2.1 sos-python=0.20.2 nbdime=4.0.1 ipywidgets=8.1.5 python-kubernetes=29.0.0 yarn nodejs=18.20.5 copier=9.3.1 jinja2-time=0.2.0 typing-extensions=4.12.2 jinja2=3.1.5 panel=1.4.5 texlab=5.19.0 chktex=1.7.9 stackview=0.9.2 configobj=5.0.8 pydantic=2.8.2 pyyaml=6.0.2 awscli=2.17.44 jupyterlab_templates=0.5.2 jupysql=0.10.12 jupyterlab-spreadsheet-editor=0.7.2 voila=0.5.7  && \
    mamba clean --all -f -y && \
    find ${CONDA_DIR} -follow -type f -name '*.a' -delete && \
    find ${CONDA_DIR} -follow -type f -name '*.pyc' -delete && \
    find ${CONDA_DIR} -follow -type f -name '*.js.map' -delete && \
    fix-permissions "${CONDA_DIR}"

# Install pip packages that don't depend on source code
RUN pip install jupyterlab-polus-render==1.0.1 jhoauthrefresh==0.3.0 dock8r==0.1.3 imjoy-jupyterlab-extension==0.2.6 jupyter-collaboration==3.1.0  && \
    jupyter server --generate-config -y && \
    npm cache clean --force && \
    jupyter lab clean

# Installation scripts that don't depend on source code (better caching)
RUN jupyter server extension enable jhoauthrefreshRUN rm -rf /tmp/jupyter-lmod && \
    git clone https://github.com/cmd-ntrf/jupyter-lmod.git /tmp/jupyter-lmod && \
    cd /tmp/jupyter-lmod && \
    git switch jupyterlab4 && \
    echo "enableImmutableInstalls: false" > .yarnrc.yml && \
    echo "nodeLinker: node-modules" >> .yarnrc.yml && \
    pip install .RUN set -e && \
    echo "📦 Installing git-lock-sign-jlx from PyPI..." && \
    echo "🗑️  Uninstalling any existing version..." && \
    pip uninstall git-lock-sign-jlx -y || true && \
    echo "🚀 Installing from PyPI..." && \
    pip install git-lock-sign-jlx && \
    echo "📋 Listing installed extensions..." && \
    jupyter labextension list && \
    echo "🔍 Verifying server extension..." && \
    jupyter server extension list && \
    echo "🔧 Enabling server extension explicitly..." && \
    jupyter server extension enable git_lock_sign_jlx && \
    echo "✅ Installation from PyPI complete!"
# Copy source code (this should be done as late as possible for better caching)  
ADD . /opt/app/
ADD docker/jupyterlab/temp_mito-config /home/jovyan/.mito/user.json
ADD docker/jupyterlab/temp_start-notebook.sh /usr/local/bin/
ADD docker/jupyterlab/temp_start-notebook.py /usr/local/bin/
ADD docker/jupyterlab/temp_start-singleuser.sh /usr/local/bin/
ADD docker/jupyterlab/temp_start-singleuser.py /usr/local/bin/
ADD docker/jupyterlab/temp_jupyter_server_config.py /etc/jupyter/
ADD docker/jupyterlab/temp_docker_healthcheck.py /etc/jupyter/

# Fix permissions on /etc/jupyter as root
USER root
RUN fix-permissions /etc/jupyter/

# Activate Lmod and conda
ENV PS1="\u $ "
RUN touch ~/.hushlogin

# Final cleanup and setup  
RUN chown -R ${NB_UID}:${NB_GID} /home/jovyan && \
    rm -rf "${HOME}/.cache" "${HOME}/.yarn"

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID
WORKDIR /home/jovyan

# Configure container startup
EXPOSE 8888

# HEALTHCHECK documentation: https://docs.docker.com/engine/reference/builder/#healthcheck
# This healtcheck works well for `lab`, `notebook`, `nbclassic`, `server`, and `retro` jupyter commands
# https://github.com/jupyter/docker-stacks/issues/915#issuecomment-1068528799
HEALTHCHECK --interval=3s --timeout=1s --start-period=3s --retries=3 \
    CMD /etc/jupyter/docker_healthcheck.py || exit 1

# Configure container startup
CMD ["start-notebook.py"]