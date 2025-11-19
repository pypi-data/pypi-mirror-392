# Module for managing infinite context window in language models, developed by the Sapiens Technology® team.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
from setuptools import setup, find_packages
package_name = 'sapiens_file_interpreter'
version = '1.0.7'
setup(
    name=package_name,
    version=version,
    author='SAPIENS TECHNOLOGY',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'paddleocr==2.7.3',
        'paddlepaddle==2.6.1',
        'INFINITE-CONTEXT-WINDOW'
    ],
    url='https://github.com/sapiens-technology/sapiens_file_interpreter',
    license='Proprietary Software'
)
# Module for managing infinite context window in language models, developed by the Sapiens Technology® team.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
