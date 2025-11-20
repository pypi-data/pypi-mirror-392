from setuptools import setup, find_packages

setup(
    name='qkbind',
    version='0.1.1',
    description='Lightweight Python bindings for C',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    url='https://github.com/yourusername/qkbind',
    packages=find_packages(),
    package_data={
        'qkbind': ['*.h'],
    },
    include_package_data=True,
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: C',
        'Programming Language :: Python :: 3',
    ],
)
