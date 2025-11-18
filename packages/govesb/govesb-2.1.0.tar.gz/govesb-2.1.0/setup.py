from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='govesb',
    version='2.1.0',
    packages=find_packages(),
    install_requires=[
        'cryptography>=44.0.0',
        'requests>=2.32.0',
        'xmltodict>=0.14.0',
    ],
    python_requires='>=3.7',
    author='Lawrance Massanja',
    license='BSD 3-Clause License',
    author_email='massanjal4@gmail.com',
    description='A Python library for supporting GovESB (Government Enterprise Service Bus) Integration',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/LarryMatrix/govesb',
    project_urls={
        'Bug Reports': 'https://github.com/LarryMatrix/govesb/issues',
        'Source': 'https://github.com/LarryMatrix/govesb',
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Security :: Cryptography',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    keywords='govesb esb enterprise-service-bus government integration cryptography rsa ecc',
)
