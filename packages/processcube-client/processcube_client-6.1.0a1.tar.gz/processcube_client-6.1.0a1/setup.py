import setuptools
import re

# TODO: mm - twine benutzen https://pypi.org/project/twine/
#
# Kurzanleitung
#    https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56


def parse_requirements(filename):
    """Parse requirements file directly without using pip private APIs"""
    requirements = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                requirements.append(line)
    return requirements


installed_reqs = parse_requirements('requirements.txt')

with open("README.md", "r") as fh:
    long_description = fh.read()

# Normalize version string to be PEP 440 compliant
# CI tools might generate versions like '6.0.5-main-hash-random' which are invalid
# This fixes them to be valid: '6.0.5.dev0' for non-primary branches
raw_version = '6.1.0-alpha.1'
if '-main-' in raw_version or '-develop-' in raw_version:
    # Extract base version and convert to dev version
    base_version = raw_version.split('-')[0]
    if '-develop-' in raw_version:
        version = f"{base_version}.dev0"
    else:
        # For main branch, just use base version
        version = base_version
elif '-beta-' in raw_version:
    # Convert beta format: '6.0.4-beta-hash' to '6.0.4b1'
    parts = raw_version.split('-')
    version = f"{parts[0]}b1"
else:
    version = raw_version

setuptools.setup(
    name='processcube_client',
    version=version,
    author="5Minds IT-Solutions GmbH & Co. KG",
    author_email="ProcessCube@5Minds.de",
    description="A Client for the workflow engine of the ProcessCube platform.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="workflow-engine atlas-engine client bpmn",
    url="https://github.com/5minds/processcube_client.py",
    packages=setuptools.find_packages(),
    install_requires=installed_reqs,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
