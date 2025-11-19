from setuptools import setup, find_packages

setup(
    name='consul-async-register',
    version='0.0.1',
    packages=find_packages(),
    install_requires=["aiohttp>=3.8.9",],
    description='Lightweight asynchronous microservices Registration module in HashiCorp Consul',
    author='TheAtrii',
)
