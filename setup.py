from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in create_a_moment/__init__.py
from create_a_moment import __version__ as version

setup(
	name="create_a_moment",
	version=version,
	description="-",
	author="ALYF GmbH",
	author_email="hallo@alyf.de",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
