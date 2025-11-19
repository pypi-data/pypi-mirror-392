from setuptools import setup, find_packages

setup(
    name='webei',
    version='0.2.0',
    description='A Python-native UI kit for creating interactive web frontends with a fluent API.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='you@example.com',
    url='https://github.com/yourusername/webei',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'webei': ['js/*.js'],
    },
    install_requires=[
        'Flask>=1.0',
        'Flask-SocketIO>=5.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Framework :: Flask',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)