
from setuptools import setup
from setuptools import find_namespace_packages

entry_points = {
    'console_scripts': [
    ],
}

TESTS_REQUIRE = [
    'nti.testing',
    'zope.testrunner',
    'coverage',
]


def _read(fname):
    with open(fname, encoding='utf-8') as f:
        return f.read()


setup(
    name='nti.traversal',
    version='1.1.0',
    author='Jason Madden',
    author_email='jason@nextthought.com',
    description="NTI Traversal",
    long_description=(
        _read('README.rst')
        + '\n\n'
        + _read("CHANGES.rst")
    ),
    url="https://github.com/OpenNTI/nti.traversal",
    license='Apache',
    keywords='Traversal',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    zip_safe=True,
    packages=find_namespace_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'repoze.lru',
        'zope.component',
        'zope.interface',
        'zope.location',
        'zope.traversing',
    ],
    extras_require={
        'test': TESTS_REQUIRE,
        'zodb': [
            'zope.container',
        ],
        'docs': [
            'Sphinx >= 2.1',
            'repoze.sphinx.autointerface',
            'sphinx_rtd_theme',
        ] + TESTS_REQUIRE,
    },
    entry_points=entry_points,
    python_requires=">=3.12",
)
