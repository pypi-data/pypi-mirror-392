# Module for managing infinite context window in language models, developed by the Sapiens Technology® team.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
from setuptools import setup, find_packages
package_name = 'INFINITE_CONTEXT_WINDOW'
version = '3.0.0'
setup(
    name=package_name,
    version=version,
    author='SAPIENS TECHNOLOGY',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'TTS',
        'paddlepaddle',
        'utilities-nlp',
        'perpetual-context-window',
        'infinite-context',
        'perpetual-context'
    ],
    url='https://github.com/sapiens-technology/INFINITE_CONTEXT_WINDOW',
    license='Proprietary Software'
)
# Module for managing infinite context window in language models, developed by the Sapiens Technology® team.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
