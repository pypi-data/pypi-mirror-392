from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r', encoding="UTF-8") as f:
        return f.read()


setup(
    name='textverified_async',
    version='0.0.2',
    author='keynet',
    author_email='viktorplay377@gmail.com',
    description='A simple asynchronous Python API client for working with the Textverified REST API',
    long_description=readme(),
    long_description_content_type='text/markdown',
    #url='not included',
    packages=find_packages(),
    install_requires=['aiohttp', 'pydantic'],
    classifiers=[
    'Programming Language :: Python :: 3.10',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
    ],
    keywords='textverified api client async asynchronous ',
    project_urls={
    'GitHub': 'https://github.com/Keynet123'
    },
    python_requires='>=3.9'
)