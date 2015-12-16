Fukei
=============

A Python Tornado port of socks proxy


Usage
-----

First, make sure you have Python 2.6 or 2.7 (supports windows).

::

    $ python --version
    Python 2.7.6

Install Fukei.

::

    python setup.py  install

Create a file named ``config.json``, with the following content.

::

    {
        "server":"my_server_ip",
        "server_port":8388,
        "local_port":1080,
        "password":"barfoo!",
        "timeout":600,
        "method":'table'
    }

Explanation of the fields:

::

    usage: usage: PROG [options]
	optional arguments:
	  -h, --help            show this help message and exit
	  -s SERVER, --server SERVER
	                        Remote server, IP address or domain (default
	                        '127.0.0.1')
	  -k PASSWORD, --password PASSWORD
	                        Password, should be same in client and server sides
	                        (default 'Keep Your Password')
	  -c FILE, --config FILE
	                        config.json path (default
	                        '/Fukei/bin/../config/config.json')
	  -p SERVER_PORT, --server-port SERVER_PORT
	                        Remote server port (default 8388)
	  -l LOCAL_PORT, --local-port LOCAL_PORT
	                        Local client port (default 1081)
	  -m METHOD, --method METHOD
	                        Encryption method (default 'aes-128-cfb')
	  -t TIMEOUT, --timeout TIMEOUT
	                        connection timeout (default 60)
	  -d, --debug           open debug mode (default False)
	  -v VERSION, --version VERSION
	                        Show Fukei version 0.1

``cd`` into the directory of ``config.json``. Run ``ss-server`` on your
server. To run it in the background, run ``nohup ss-server > log &``.

On your client machine, run ``ss-local``.

Change the proxy settings in your browser to

::

    protocol: socks5
    hostname: 127.0.0.1
    port:     your_local_port

Command line args
-----------------

You can pass command line arguments to override settings from ``config.json``.

::

    ss-local -s server_name -p server_port -l local_port -k password -m bf-cfb
    ss-server -p server_port -k password -m bf-cfb
    ss-server -c /etc/fukei/config.json

Encryption
----------

If you want to use non-default encryption methods like "bf-cfb", please
install `M2Crypto <http://chandlerproject.org/Projects/MeTooCrypto>`__.

Ubuntu:

::

    sudo apt-get install python-m2crypto

Others:

::

    pip install M2Crypto

Requirements
-----------

You must to install Tornado (requires version 3.0+).

::

    $ sudo apt-get install python-tornado

Or:

::

    $ sudo pip install tornado


And if using python2.6, you need to install argparse for python2.6

::

	$ sudo pip install argpasre


Alert
---------------

Tornado IOStream doesn't support timeout.
Hence the timeout setting is useless in this case.


License
-------

MIT
