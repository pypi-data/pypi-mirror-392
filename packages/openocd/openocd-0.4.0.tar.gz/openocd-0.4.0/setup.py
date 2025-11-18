# SPDX-License-Identifier: LGPL-2.1-or-later

import setuptools

with open('README.md', 'r') as fd:
    long_description = fd.read()

setuptools.setup(
    name='openocd',
    version='0.4.0',
    description='Python interface library for OpenOCD',
    long_description=long_description,
    keywords='OpenOCD microcontroller debug embedded',
    long_description_content_type='text/markdown',
    author='Marc Schink',
    author_email='dev@zapb.de',
    url='https://gitlab.zapb.de/openocd/python-openocd',
    project_urls={
        'Source': 'https://gitlab.zapb.de/openocd/python-openocd',
    },
    license='LGPL-2.1-or-later',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Embedded Systems',
    ],
    package_dir={"": "src"},
    install_requires=[
        'typing_extensions >= 4.5.0',
    ],
    packages=setuptools.find_packages(where="src"),
    python_requires='>=3.10',
)
