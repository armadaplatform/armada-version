from armada import hermes
from tornado.ioloop import IOLoop
from tornado.web import Application, url

from handlers import VersionCheckHandler, IndexHandler


def main():
    config = hermes.get_config('config.json', {})
    debug = config.get('debug', False)
    app = Application(
        (
            url('/', IndexHandler),
            url('/version_check', VersionCheckHandler),
        ),
        debug=debug
    )
    app.listen(80)
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
