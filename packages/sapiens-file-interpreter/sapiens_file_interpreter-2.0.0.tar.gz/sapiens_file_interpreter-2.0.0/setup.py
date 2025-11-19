# Module for managing infinite context window in language models, developed by the Sapiens Technology® team.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
from setuptools import setup, find_packages
package_name = 'sapiens_file_interpreter'
version = '2.0.0'
setup(
    name=package_name,
    version=version,
    author='SAPIENS TECHNOLOGY',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'paddleocr',
        'paddlepaddle',
        'INFINITE-CONTEXT-WINDOW'
    ],
    url='https://github.com/sapiens-technology/sapiens_file_interpreter',
    license='Proprietary Software'
)
# Module for managing infinite context window in language models, developed by the Sapiens Technology® team.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
