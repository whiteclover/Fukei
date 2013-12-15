from setuptools import setup 


with open('README.rst') as f:
    long_description = f.read()

setup(
    name = "fukei",
    version = "0.1",
    license = 'MIT',
    description = "A Python Tornado port of shadowsocks and socks proxy",
    author = 'Thomas Huang',
    url = 'https://github.com/thomashuang/Fukei',
    packages = ['fukei'],
    package_data={
        'fukei': ['README.rst', 'LICENSE', 'config/config.json']
    },
    install_requires = ['setuptools',
                        ],
    entry_points="""
    [console_scripts]
    ss-local = bin/ss-local
    sss-erver = bin/ss-server
    """,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: Proxy Servers',
        ],
    long_description=long_description,
)