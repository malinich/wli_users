import traceback

import tornado.web


class BaseHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    @property
    def db_instance(self):
        return self.application.db_instance

    @property
    def payload(self) -> dict:
        return tornado.escape.json_decode(self.request.body)

    def write_error(self, status_code, **kwargs):
        self.set_header("Content-Type", "application/json")

        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            self.set_header('Content-Type', 'text/plain')
            for line in traceback.format_exception(*kwargs["exc_info"]):
                self.write(line)
            self.finish()
        else:
            self.finish({
                "code": status_code,
                "message": self._reason,
            })
