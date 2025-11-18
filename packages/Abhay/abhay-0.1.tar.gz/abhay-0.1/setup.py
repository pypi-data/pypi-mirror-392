from setuptools import setup,find_packages

setup(
    name='Abhay',
    version= '0.1',
    author='OM',
    author_email= 'abhayvermaav389@gmail.com',
    description='this is speechToText pakage craeted by OM '
)
packages =find_packages(),
install_requirements = [
    'selenium',
    'webdriver_manager'
]

