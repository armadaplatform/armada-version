from armada import hermes
from tornado.ioloop import IOLoop
from tornado.web import Application, url
from tornado.log import enable_pretty_logging

from handlers import VersionCheckHandler, IndexHandler


def main():
    enable_pretty_logging()

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
