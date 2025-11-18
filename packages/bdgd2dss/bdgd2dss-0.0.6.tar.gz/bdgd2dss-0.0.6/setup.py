from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name='bdgd2dss',
    version='0.0.6',
    license='MIT License',
    author='Arthur Gomes de Souza',
    author_email='arthurgomesba@gmail.com',
    maintainer='Wellington Maycon Santos Bernardes',
    maintainer_email='wmsbernardes@ufu.br',
    description=u'Ferramenta para modelagem de alimentadores da BDGD para uso com OpenDSS',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='bdgd2dss bdgd',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=[
        'pandas==2.3.3'
    ],
)
