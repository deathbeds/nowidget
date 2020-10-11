import monkeytype.stubs
import nowidget
import traitlets
import IPython


class Trace(nowidget.Trait):
    collector = traitlets.Any()
    trace = traitlets.Any()
    traces = traitlets.List()
    max_dict_size = traitlets.Integer(1000)

    def log(self, trace):
        self.traces.append(trace)

    def flush(self):
        self.flushed = True

    def __enter__(self):
        self.trace = monkeytype.tracing.trace_calls(
            self, self.max_dict_size, lambda c: c.co_filename.startswith(
                '<ipython-input-')
        )
        self.toggle(True)
        self.trace.__enter__()

    def __exit__(self, type=None, object=None, traceback=None):
        self.toggle(False)
        self.trace.__exit__(type, object, traceback)

    def stub(self, line=None, cell=None):
        # if line is None:
        return {k: v.render() for k, v in monkeytype.stubs.build_module_stubs_from_traces(
            self.traces, self.max_dict_size).items()}

    on = __enter__
    off = __exit__


def retype(logger):
    import retype
    src = '\n'.join(map(
        __import__('inspect').getsource, set(_.func for _ in logger.data if hasattr(_, 'func'))))
    retype.Config.incremental, retype.Config.replace_any = False, True
    src = retype.lib2to3_parse(src)
    retype.reapply(__import__('typed_ast').ast3.parse(
        logger.stubs()).body, src)
    retype.fix_remaining_type_comments(src)
    return retype.lib2to3_unparse(src, hg=False)


def load_ipython_extension(shell):
    if not shell.has_trait('trace'):
        shell.add_traits(trace=traitlets.Instance(
            Trace, kw=dict(parent=shell)
        ))
        shell.trace.register()


def unload_ipython_extension(shell):
    shell.trace.unregister()
    ...
