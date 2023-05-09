import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pyCOSETC',
    version='0.0.1',
    author='Sameer',
    author_email='sameeresque@protonmail.com',
    description='Exposure Time Calculator for HST/COS',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/sameeresque/pyCOSETC',
    project_urls = {
        "Bug Tracker": "https://github.com/sameeresque/pyCOSETC/issues"
    },
    license='MIT',
    packages=['etc'],
    install_requires=['numpy','astropy','astroquery','bs4','selenium'],
)
