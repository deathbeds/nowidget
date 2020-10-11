import abc
import nowidget


class MetaState(abc.ABCMeta):
    def __bool__(self):
        return self.validate(nowidget.util.get_caller_namespace())

    @abc.abstractclassmethod
    def validate(self, globals): ...


class RunningState(metaclass=MetaState):
    def __new__(cls, *args, **kwargs):
        raise TypeError(F"can't initialize {cls}")


class MAIN(RunningState):
    @classmethod
    def validate(cls, globals):
        if globals.get("__name__", None) != '__main__':
            return False
        return True


class IPYTHON(RunningState):
    @classmethod
    def validate(cls, globals):
        import sys
        if "IPython" not in sys.modules:
            return False
        import IPython
        return bool(IPython.get_ipython())


class PYTEST(RunningState):
    @classmethod
    def validate(cls, globals):
        return nowidget.util.in_pytest()
