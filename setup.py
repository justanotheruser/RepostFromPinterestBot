import pathlib
import subprocess

from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install

__requires__ = ['pipenv']

packages = find_packages(exclude=['tests'])
base_dir = pathlib.Path(__file__).parent

pipenv_command = ['pipenv', 'install', '--deploy', '--system']
pipenv_command_dev = ['pipenv', 'install', '--dev', '--deploy', '--system']


class PostDevelopCommand(develop):
    """Post-installation for development mode."""

    def run(self):
        subprocess.check_call(pipenv_command_dev)
        develop.run(self)


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        subprocess.check_call(pipenv_command)
        install.run(self)


setup(
    name='repost_from_pinterest_bot',
    use_scm_version=True,
    packages=packages,
    setup_requires=['setuptools_scm'],
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
)