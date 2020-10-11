"""interactive for the IPython shell."""

import nowidget
import jinja2.meta
import IPython
import sys
import traitlets
import functools

__all__ = "Template",


ENVIRONMENT = None


def environment(shell=None) -> jinja2.Environment:
    """create a global jinja2 environment."""
    global ENVIRONMENT
    if ENVIRONMENT is None:
        try:
            ENVIRONMENT = __import__(
                'nbconvert').exporters.TemplateExporter().environment
        except ModuleNotFoundError:
            ENVIRONMENT = jinja2.Environment()
        ENVIRONMENT.loader.loaders.append(jinja2.FileSystemLoader('.'))
        ENVIRONMENT.finalize = Finalize(parent=shell or IPython.get_ipython())
    return ENVIRONMENT


class Template(nowidget.Display):
    body = traitlets.Unicode()
    template = traitlets.Any()
    environment = traitlets.Any()
    globals = traitlets.Dict()

    def __init__(self, body: str, **kwargs):
        super().__init__(body=body, **kwargs)
        if not self.parent.has_trait('display_manager'):
            nowidget.manager.load_ipython_extension(self.parent)
        self.parent.display_manager.append(self)

    @traitlets.default('template')
    def _default_template(self):
        return self.environment.from_string(self.body)

    @traitlets.default('environment')
    def _default_environment(self):
        return environment()

    @traitlets.default('vars')
    def _default_vars(self):
        return jinja2.meta.find_undeclared_variables(self.template.environment.parse(self.body))

    def render(self, **kwargs):
        return self.template.render(
            {**(kwargs or self.parent.user_ns), **self.globals}
        )

    def main(self, **kwargs):
        return IPython.display.Markdown(self.render(
            **{**(kwargs or self.parent.user_ns), **self.globals}
        ))


class Finalize(nowidget.Trait):
    """a callable trait that uses the current ipython shell
    to update jinja2 templates."""

    def normalize(self, type, object, metadata) -> str:
        """normalize and object with (mime)type and return a string."""
        if type == 'text/html' or 'svg' in type:
            object = nowidget.util.minify(object)

        if type.startswith('image'):
            width, height = metadata.get(type, {}).get(
                'width'), metadata.get(type, {}).get('height')
            object = nowidget.util.encode(object)
            object = F"""<img src="data:image/{type.partition('/')[2]};base64,{object}"/>"""
        return object

    def __call__(self, object):
        """try to convert the object into a markdown or html
        representation using the current ipython shell."""
        if not self.enabled:
            return object
        datum = self.parent.display_formatter.format(object)
        data, metadata = datum if isinstance(datum, tuple) else (datum, {})
        try:
            key = next(filter(data.__contains__,
                              nowidget.util.active_types(self.parent)))
        except StopIteration:
            return str(object)
        if key == 'text/plain':
            return str(object)
        return self.normalize(key, data[key], metadata)
