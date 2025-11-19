from setuptools import setup, find_packages

setup(
    name='perf-sentinel',
    version='0.1.0',
    packages=find_packages(exclude=['tests', 'tests.*', 'examples', 'examples.*']),
    description='Long-term performance testing and monitoring system for Python',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/PerfSentinel',
    author='Your Name',
    author_email='your.email@example.com',
    license='MIT',
    python_requires='>=3.8',
    install_requires=[
        'schedule>=1.2.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'black>=23.0.0',
            'mypy>=1.0.0',
        ],
        'profiling': [
            'py-spy>=0.3.14',
            'aioflame>=0.1.0',
        ],
        'all': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'black>=23.0.0',
            'mypy>=1.0.0',
            'py-spy>=0.3.14',
            'aioflame>=0.1.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'perf-sentinel=perf_sentinel.ci.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: System :: Monitoring',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    keywords='performance testing profiling monitoring async asyncio',
    project_urls={
        'Documentation': 'https://github.com/YolieDeng/PerfSentinel',
        'Source': 'https://github.com/YolieDeng/PerfSentinel',
        'Bug Reports': 'https://github.com/YolieDeng/PerfSentinel/issues',
    },
)
