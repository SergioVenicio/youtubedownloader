import os

from sanic import Sanic
import jinja2

from instance import config


CONFIGS = {
    'DEV': config.BaseConfig,
    'PROD': config.ProdConfig
}


async def template(template_file, **kwargs):
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_path = os.path.join(base_path, 'templates/')
    templates_loader = jinja2.FileSystemLoader(searchpath=templates_path)
    templates_env = jinja2.Environment(loader=templates_loader)
    template = templates_env.get_template(template_file)
    return template.render(kwargs)


def create_app():
    app = Sanic(__name__)

    __config = CONFIGS[os.environ.get('APP_MODE', 'PROD')]

    app.config.from_object(__config)

    return app


app = create_app()

