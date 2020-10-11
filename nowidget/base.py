import sys
import nowidget
import functools
import traitlets
import IPython
import functools

REGISTER_KEYS = "pre_execute pre_run_cell post_run_cell post_execute".split()


class Trait(traitlets.HasTraits):
    parent = traitlets.Any()

    @traitlets.default('parent')
    def _default_parent(self): return IPython.get_ipython()

    enabled = traitlets.Bool(True)

    def register(self):
        if self.parent:
            for key in REGISTER_KEYS:
                if hasattr(self, key):
                    self.parent.events.register(key, getattr(self, key))

    def unregister(self):
        if self.parent:
            for key in REGISTER_KEYS:
                if hasattr(self, key):
                    self.parent.events.unregister(key, getattr(self, key))

    def toggle(self, object: bool):
        self.enabled = bool(
            object if object is None else not self.enabled)

    on = functools.partialmethod(toggle, True)
    off = functools.partialmethod(toggle, False)


class Display(Trait):
    vars = traitlets.Any()
    id = traitlets.Any()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register()

    def register(self):
        if self.parent:
            self.enabled and self.parent.display_manager.append(self)
        super().register()

    def unregister(self):
        super().unregister()
        if self.parent:
            self.parent.display_manager.pop(self)

    def update(self, **kwargs):
        if not self.enabled:
            return
        if self.id is None:
            return

        self.id.update(self.main(**kwargs))

    def display(self, **kwargs):
        object = self.main(**kwargs)
        if object is None:
            return
        if self.vars:
            if self.id is None:
                self.id = IPython.display.display(
                    object, display_id=True)
            else:
                self.id.display(object)
        else:
            IPython.display.display(object)

    _ipython_display_ = display


class DisplayManager(Trait):
    display = traitlets.Dict()
    state = traitlets.Dict()
    widgets = traitlets.List()

    def pre_execute(self):
        deleted = getattr(self.parent, '_last_parent', {}).get(
            'metadata', {}).get('deletedCells', [])
        for key, displays in self.display.items() if deleted else []:
            self.display[key] = [
                x for x in displays if x.id and x.id.display_id not in deleted
            ]

    def append(self, object):
        for key in object.vars or []:
            self.display[key] = self.display.get(key, [])
            self.display[key].append(object)
            self.state[key] = self.parent.user_ns.get(key, None)

    def pop(self, object):
        for key, values in self.display.items():
            self.display[key] = [x for x in values if x is not object]

    def _post_execute_widget(self, object, change):
        with object.hold_trait_notifications():
            self.post_execute()

    def post_execute(self):
        if not self.enabled:
            return
        update = {
            x: self.parent.user_ns.get(x, None) for x in self.display
            if x == "__test__" or nowidget.util.isinteractive(self.parent.user_ns.get(x, None)) or
            self.parent.user_ns.get(x, None) is not
            self.state.get(x, None)
        }
        for key, object in update.items():
            if nowidget.util.isinteractive(object) and object not in self.widgets:
                object.observe(functools.partial(
                    self._post_execute_widget, object))
                self.widgets += [object]
        self.state.update(update)
        for object in set(
            sum([self.display[x] for x in update], [])
        ):
            if not object.enabled:
                continue
            try:

                object.update(**self.state)

            except Exception as e:
                self.pop(object)
                sys.stderr.writelines(str(self.state))
                sys.stderr.writelines(str(e).splitlines())


def load_ipython_extension(shell):
    if not shell.has_trait('display_manager'):
        shell.add_traits(display_manager=traitlets.Instance(
            DisplayManager, kw=dict(parent=shell)
        ))
        shell.display_manager.register()


def unload_ipython_extension(shell):
    shell.display_manager.unregister()
    ...
