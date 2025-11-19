from setuptools import setup, find_packages

setup(
    name='metasheller',
    version='0.1.1',    
    install_requires=[
        'scanpy',
        'numpy',
        'pandas',
        'SEACells',
        'enlighten',
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
)