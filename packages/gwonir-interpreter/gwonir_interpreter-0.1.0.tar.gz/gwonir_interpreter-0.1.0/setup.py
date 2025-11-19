from setuptools import setup, find_packages

setup(
    name='gwonir-interpreter',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    author='Your Name',
    description='A simple interpreter for the Gwonir programming language.',
    long_description='Gwonir language interpreter implemented in Python.',
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/gwonir_interpreter_project',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': [
            'gwonir=gwonir_interpreter.gwonir_core:main',
        ],
    },
)