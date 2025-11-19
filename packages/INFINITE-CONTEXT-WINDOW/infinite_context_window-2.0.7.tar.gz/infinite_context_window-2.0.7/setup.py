# Module for managing infinite context window in language models, developed by the Sapiens Technology® team.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
from setuptools import setup, find_packages
package_name = 'INFINITE_CONTEXT_WINDOW'
version = '2.0.7'
setup(
    name=package_name,
    version=version,
    author='SAPIENS TECHNOLOGY',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'TTS==0.22.0',
        'paddlepaddle==2.6.1',
        'utilities-nlp==6.0.2',
        'perpetual-context-window==4.0.5',
        'infinite-context==3.0.4',
        'perpetual-context==2.0.3'
    ],
    url='https://github.com/sapiens-technology/INFINITE_CONTEXT_WINDOW',
    license='Proprietary Software'
)
# Module for managing infinite context window in language models, developed by the Sapiens Technology® team.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
