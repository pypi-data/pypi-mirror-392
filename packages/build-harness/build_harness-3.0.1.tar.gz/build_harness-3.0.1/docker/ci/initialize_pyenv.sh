#!/bin/bash
#
#
# Copyright (c) 2024 Russell Smiley
#
# This file is part of build_harness.
#
# You should have received a copy of the MIT License along with build_harness.
# If not, see <https://opensource.org/licenses/MIT>.
#
#

# install necessary apt packages
apt-get update
xargs -a "${requirements_lock}" \
  apt-get install \
    -y \
    --no-install-recommends
rm -rf /var/lib/apt/lists/*

# initialize git for later when using git operations in CI
# NOTE: Assumption here is that there are no permanent (push) git operations
#       being performed in CI
git config --global user.email "you@example.com"
git config --global user.name "Your Name"

# install pyenv
source /pyenv-installer

command -v pyenv >/dev/null || export PATH="${PYENV_ROOT}/bin:${PATH}"
# install the necessary python version
pyenv install ${python_version}

# initialize the pyenv python shell
eval "$(pyenv init -)"; \
pyenv shell ${python_version}

# install project dependencies
python3 -m venv ${venv_path}
${venv_path}/bin/pip install "${project_dir}[dev,doc,test]"
