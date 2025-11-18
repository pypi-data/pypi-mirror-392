from setuptools import setup, find_packages
import pathlib
import io

HERE = pathlib.Path(__file__).parent
long_description = """
VS Server Colab

Command-line helpers to install, start and teardown a code-server (VS Code in browser)
and expose it via ngrok.
"""

setup(
    name='vs-server-colab',
    version='1.0.0',
    description='Expose a code-server instance over ngrok',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hasinthaka/vs-server-script',
    author='Hasinthaka',
    license='MIT',
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'vscolab=vs_server_colab.cli:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux'
    ],
    python_requires='>=3.8',
)
