#!/bin/bash
# Bamboo CI script to build the Sphinx documentation
# Note: this script should be run from the root of the git repository

# Debuggging:
set -e -o pipefail
echo "Loading modules..."

# Set up environment such that module files can be loaded
. /etc/profile.d/modules.sh
module purge
# Load modules required for building the Sphinx documentation
# - Saxon (required for building the DD)
# - Python
# - GitPython (providing `git` package), needed for the changelog
# - IMASPy (providing `imaspy` package), needed for the changelog
module load \
    Saxon-HE/12.4-Java-21 \
    Python/3.11.5-GCCcore-13.2.0 \
    IMASPy/1.1.0-foss-2023b


# Debuggging:
echo "Done loading modules"
set -x

# Create Python virtual environment
rm -rf venv
python -m venv --system-site-packages venv
source venv/bin/activate

# Install dependencies
pip install -r docs/requirements.txt

# Debugging:
pip freeze

# Try to update the pull_requests.json with a Bitbucket server API call:
if [ -z "${IMAS_DD_BITBUCKET_TOKEN:+x}${bamboo_IMAS_DD_BITBUCKET_TOKEN:+x}" ]; then
    echo '$IMAS_DD_BITBUCKET_TOKEN is not set, cannot create changelog!'
    echo 'Please set environment variable $IMAS_DD_BITBUCKET_TOKEN to a token with read'
    echo 'access to https://git.iter.org/projects/IMAS/repos/data-dictionary/browse'
    echo 'See https://confluence.iter.org/display/IMP/How+to+access+repositories+with+access+token'
else
    echo 'Updating pull_requests.json ...'
    cd docs
    python -m sphinx_dd_extension.dd_changelog_helper
    cd ..
fi

# Set sphinx options:
# - `-D dd_changelog_generate=1`: generate and build the changelog
# - `-D dd_autodoc_generate=1`: generate and build the IDS reference
# - `-W`: turn warnings into errors
# - `--keep-going`: with -W, keep going when getting warnings
export SPHINXOPTS="-D dd_changelog_generate=1 -D dd_autodoc_generate=1 -W --keep-going"

# Build the sphinx documentation
make sphinx

# Output the version, used by the deployment script for tagged releases:
git describe > docs/_build/html/version.txt
