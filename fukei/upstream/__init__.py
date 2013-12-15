from fukei.utils import import_class


__streams = {

    'default': lambda: (import_class('fukei.upstream.remote.RemoteUpstream'),
                        import_class('tornado.iostream.IOStream')),
    'local': lambda: (import_class('fukei.upstream.local.LocalUpstream'),
                      import_class('tornado.iostream.IOStream')),
    'remote': lambda: (import_class('fukei.upstream.remote.RemoteUpstream'),
                       import_class('fukei.upstream.local.CryptoIOStream')),
}


def get_streams(name):
    return __streams.get(name, None)
