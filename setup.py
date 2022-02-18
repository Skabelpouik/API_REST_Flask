from setuptools import setup

setup(
    name='SCRAP_API',
    version='1.0',
    long_description=__doc__,
    packages=['SCRAP_API'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask']
)