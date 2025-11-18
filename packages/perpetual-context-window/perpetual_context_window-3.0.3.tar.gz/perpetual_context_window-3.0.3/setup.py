# Module developed by Sapiens Technology® for building language model algorithms with a perpetual context window without complete forgetting of initial, intermediate, and final information.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
from setuptools import setup, find_packages
package_name = 'perpetual_context_window'
version = '3.0.3'
setup(
    name=package_name,
    version=version,
    author='SAPIENS TECHNOLOGY',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'infinite-context',
        'perpetual-context',
        'sapiens-infinite-context-window',
        'certifi'
    ],
    url='https://github.com/sapiens-technology/perpetual_context_window',
    license='Proprietary Software'
)
# Module developed by Sapiens Technology® for building language model algorithms with a perpetual context window without complete forgetting of initial, intermediate, and final information.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
