#!/usr/bin/env python


from fukei.utils import import_class


__connections = {

    'default': lambda: import_class('fukei.connection.base.Socks5Connection'),
    'local': lambda: import_class('fukei.connection.local.LocalConnection'),
    'remote': lambda: import_class('fukei.connection.remote.RemoteConnection'),
}


def get_connection(name):

    return __connections.get(name, None)
