from setuptools import setup, find_packages

setup(
    name='pysyscore',
    version='0.1.0',
    packages=find_packages(),
    description='Low-level, native Windows system access wrappers for Python administration scripts.',
    author='AI Assistant',
    license='MIT',
    
    # Required dependency for service management functionalities
    install_requires=[
        'pywin32', 
    ],
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.9',
        'Topic :: System :: Systems Administration',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
)
