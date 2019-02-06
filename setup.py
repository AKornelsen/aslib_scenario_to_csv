# NOTE please note that this config needs to be changed, since the ASlib package can't be used within the dependency links.

from pip.req import parse_requirements
from setuptools import setup, find_packages

required_package_links = []
required_packages = []

requirements = [str(item) for item in parse_requirements("requirements.txt", session=False)]

for item in requirements:
    if 'git+' in item:
        required_package_links.append(str(item).replace('git+', ''))
    if item.req:
        required_packages.append(str(item.req))

setup(
    name='AsLibToKebi',
    version='0.1',
    url='https://github.com/AKornelsen/aslib_scenario_to_csv.git',
    license='MIT',
    author='Andreas Kornelsen',
    author_email='',
    description='Transform ASlib scenarios to KEBI formatted datasets.',
    long_description=open('README.md').read(),
    packages=find_packages(exclude=['aslib_data-aslib-v4.0', 'test']),
    include_package_data=True,
    platforms='any',
    install_requires=required_packages,
    dependency_links=required_package_links,
    entry_points={
        "console_scripts": [
            "program = program.module:main"
        ]
    }
)
