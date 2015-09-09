from setuptools import find_packages, setup

setup(
    name='django-youtube-api',
    version=__import__('youtube_api').__version__,
    description='Django implementation for youtube API',
    long_description=open('README.md').read(),
    author='krupin.dv',
    author_email='krupin.dv19@gmail.com',
    url='https://github.com/ramusus/django-youtube-api',
    download_url='http://pypi.python.org/pypi/django-youtube-api',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,  # because we're including media that Django needs
    install_requires=[
        'google-api-python-client',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
