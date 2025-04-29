from setuptools import find_packages, setup
import os
work_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(work_dir,'README.md'),'r') as f:
    long_description = f.read()

setup(
    name='ind',
    version='0.0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ind = ind.main:main',
        ],
    },
    description='Investigational New Drug (IND) Application',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/marczepeda/ind',
    author='Marcanthony Zepeda',
    author_email='marczepeda18@gmail.com',
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['numpy',
                      'matplotlib',
                      'seaborn',
                      'pandas',
                      'requests',
                      'scipy',
                      'statsmodels',
                      'scikit-learn',
                      'adjustText',
                      'openbb'],
    python_requires='>=3.11'
)