import os

from setuptools import setup


def open_file(filename):
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filename),
        mode='r',
        encoding='utf-8',
    ) as f:
        return f.read()


setup(
    name='pydapters',
    version='0.0.1',
    description='Data transformation library',
    long_description=open_file('README.md'),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
    ],
    author='Andrey Shevchuk',
    author_email='angru@list.ru',
    url='https://github.com/angru/pydapters',
    license='MIT',
    packages=['pydapters'],
    python_requires='>=3.6',
)
