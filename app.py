import asyncio
import re

import tornado.platform.asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from tornado.web import Application
from umongo.document import MetaDocumentImplementation
from umongo.frameworks import MotorAsyncIOInstance
from umongo.template import MetaTemplate

import settings
from utils import Router


class WliApplication(Application):
    db = AsyncIOMotorClient(settings.MONGO_HOST).wli
    db_instance = MotorAsyncIOInstance()
    db_instance.init(db)

    def __init__(self):
        self.register_apps()
        handlers = self.configure_handlers()

        super(WliApplication, self).__init__(handlers)

    def register_apps(self):
        for app_path in settings.APPS:
            __import__(app_path, globals(), locals(), ['models'])

    def configure_handlers(self):
        for app_path in settings.APPS:
            __import__(app_path, globals(), locals(), ['handlers'])
        return Router.get_routes()


class MetaBaseModel(type):
    def __new__(cls, name, bases, attrs: dict, **kwargs):
        klass = super().__new__(cls, name, bases, attrs, **kwargs)
        if '__collection__' in attrs:
            attrs['Meta'].collection = getattr(cls.db(),
                                               attrs['__collection__'])
        db_instance = cls.db_instance()
        klass = db_instance.register(klass)
        return klass

    @staticmethod
    def db():
        return WliApplication.db

    @staticmethod
    def db_instance():
        return WliApplication.db_instance


class MetaBaseTemplate(MetaBaseModel, MetaTemplate):
    class Meta:
        pass


def main():
    return WliApplication()


async def create_index():
    for app_path in settings.APPS:
        models = __import__(app_path, globals(), locals(), ['models']).models

        for name in (m for m in dir(models) if re.match(r'[A-Z]', m)):
            model = getattr(models, name)

            if isinstance(model, MetaDocumentImplementation) and \
                    hasattr(model, '__collection__'):
                await model.ensure_indexes()


if __name__ == '__main__':
    app = main()
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    app.listen(3005)
    asyncio.get_event_loop().run_until_complete(create_index())
    asyncio.get_event_loop().run_forever()
    # server = tornado.httpserver.HTTPServer(app)
    # server.listen(3000)
    # tornado.ioloop.IOLoop.current().start()
