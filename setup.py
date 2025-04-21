from setuptools import setup


def parse_requirements():
    with open('requirements.txt', 'r') as f:
        return f.read().splitlines()


required_packages = parse_requirements()

APP = ['client/main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': required_packages,
    'iconfile': 'assets/logo_app_icon.icns',
}

setup(
    app=APP,
    name='Libra Lens',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=required_packages,
    version="1.0",
    author="Elias Guralnik",
)
