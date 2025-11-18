from setuptools import setup, find_packages

setup(
    name='liquipediarl',
    version='1.0.6',
    description='Liquipedia Rocket League API Wrapper',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='8pq8',
    url='https://github.com/8pq8/liquipediarl',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
    python_requires='>=3.7',
)

