"""setup file for pypi
"""
import setuptools

install_requires = [
    'requests',
    'websockets',
    'pycryptodome'
]

with open("README.md", "r", encoding='UTF-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='mojito2',
    version='0.1.2',
    author='Jonghun Yoo, Brayden Jo',
    author_email='jonghun.yoo@pyquant.co.kr, brayden.jo@pyquant.co.kr',
    description="python wrapper for korea broker's REST API services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/sharebook-kr/mojito',
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
