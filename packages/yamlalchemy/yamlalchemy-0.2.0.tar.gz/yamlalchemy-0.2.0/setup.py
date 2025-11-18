#
from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='yamlalchemy',
    version='0.2.0',
    description='YAMLAlchemy is a Python-based library to convert YAML to SQLAlchemy read-only queries.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ahmetonol/yamlalchemy',
    author='Ahmet Onol',
    author_email='onol.ahmet@gmail.com',
    license='MIT',
    packages=['yamlalchemy'],
    install_requires=[
        'PyYAML',
        'SQLAlchemy'
    ],

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.8',
)
