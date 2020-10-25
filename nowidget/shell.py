import nowidget

import traitlets
from . import kernel


class Weave(nowidget.Trait):
    def post_run_cell(self, result):
        source = result.info.raw_cell
        if source.splitlines()[0].strip():
            nowidget.Template(source, parent=self.parent).display()


def load_ipython_extension(shell):
    with __import__("tingle").Markdown():
        import tingle.extension
    if not shell.has_trait('weave'):
        shell.add_traits(weave=traitlets.Instance(
            Weave, kw=dict(parent=shell)))
        shell.weave.register()
    tingle.extension.load_ipython_extension(shell)
    nowidget.load_ipython_extension(shell)
    kernel.load_ipython_extension(shell)


def unload_ipython_extension(shell):
    if shell.has_trait('tingle'):
        shell.input_transformer_manager.cleanup_transforms = [
            x for x in shell.input_transformer_manager.cleanup_transforms
            if x != shell.tingle.__call__
        ]
    if shell.has_trait('weave'):
        shell.weave.unregister()
    nowidget.unload_ipython_extension(shell)
    import tingle
    tingle.extension.unload_ipython_extension(shell)
    kernel.unload_ipython_extension(shell)
