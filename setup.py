from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='trellogd',
    version='0.2.1',
    description='A tool for organizing your jobsearch',
    long_description=readme(),
    url='https://github.com/kmix27/trello_glassdoor',
    author='Kyle Mix',
    author_email='kyle@kylemix.com',
    license='MIT',
    py_modules=['trellogd', 'config'],
    install_requires=['beautifulsoup4>=4.4.1',
                    'fake-useragent>=0.1.4',
                    'py-trello>=0.9.0',
                    'requests>=2.12.4',
                    'argparse>=1.4.0',
                    'lxml>=3.6.0',
                    'html2text>=2016.9.19'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5'],
    keywords='job search glassdoor glass door trello organization',
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts':['tgd=trellogd:main']
    }
    )
