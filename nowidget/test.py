import traitlets
import unittest
import doctest
import re
import ast
import contextlib
import IPython
import inspect
import sys
import textwrap
import functools
import nowidget
import importlib


def collect_unittest(object):
    return unittest.defaultTestLoader.loadTestsFromTestCase(object)


def collect_function(object):
    return unittest.FunctionTestCase(object)


def collect_doctest(object, vars, name):
    doctest_suite = doctest.DocTestSuite()
    test_case = doctest.DocTestParser().get_doctest(object, vars, name, name, 1)
    test_case.examples and doctest_suite.addTest(
        doctest.DocTestCase(test_case, doctest.ELLIPSIS))
    test_case = InlineDoctestParser().get_doctest(object, vars, name, name, 1)
    test_case.examples and doctest_suite.addTest(
        doctest.DocTestCase(test_case, checker=NullOutputCheck))
    if doctest_suite._tests:
        return doctest_suite


def collect(name, *objects, alias=None, **globals) -> unittest.TestSuite:
    globals = globals or vars(importlib.import_module(name))
    name = alias or name
    suite = unittest.TestSuite()
    for object in objects:
        if isinstance(object, type) and issubclass(object, unittest.TestCase):
            object = collect_unittest(object)
        elif isinstance(object, str):
            object = collect_doctest(object, globals, name)
            object and suite.addTest(object)
            continue
        elif inspect.isfunction(object):
            object = collect_function(object)
        else:
            continue
        if object is not None:
            suite.addTest(object)
            # object = collect_doctest(object, vars, name)
            # object and suite.addTest(object)

    suite._tests = [x for x in suite._tests if x]
    return suite


def show(object: unittest.TestResult) -> str:
    body = ""
    if object.testsRun:
        if object.errors:
            body += '\n'.join(msg for text,
                              msg in object.errors)

        if object.failures:
            body += '\n'.join(msg for text,
                              msg in object.failures)
    return body if body else None


def run(suite: unittest.TestSuite) -> str:
    result = unittest.TestResult()
    with contextlib.ExitStack() as stack:
        if nowidget.IPYTHON:
            import IPython
            stack.enter_context(ipython_compiler(IPython.get_ipython()))
        suite.run(result)
    return result


class NullOutputCheck(doctest.OutputChecker):
    def check_output(self, *e): return True


class InlineDoctestParser(doctest.DocTestParser):
    _EXAMPLE_RE = re.compile(r'`(?P<indent>\s{0})'
                             r'(?P<source>[^`].*?)'
                             r'`')
    def _parse_example(self, m, name, lineno): return m.group(
        'source'), None, "...", None


@contextlib.contextmanager
def ipython_compiler(shell):
    def compiler(input, filename, symbol, *args, **kwargs):
        nonlocal shell
        return shell.compile(
            ast.Interactive(
                body=shell.transform_ast(
                    shell.compile.ast_parse(shell.transform_cell(
                        textwrap.indent(input, ' '*4)))
                ).body),
            F"In[{shell.last_execution_result.execution_count}]",
            "single",
        )

    yield setattr(doctest, "compile", compiler)
    doctest.compile = compile


class Definitions(nowidget.base.Trait, ast.NodeTransformer):
    def register(self):
        if not any(x for x in self.parent.parent.ast_transformers if isinstance(x, type(self))):
            self.parent.parent.ast_transformers.append(self)

    def unregister(self):
        self.parent.parent.ast_transformers = [
            x for x in self.parent.parent.ast_transformers if x is not self]

    def visit_FunctionDef(self, node):
        self.parent.medial_test_definitions.append(node.name)
        return node
    visit_ClassDef = visit_FunctionDef


class Test(nowidget.base.Display):
    name = traitlets.Unicode()
    alias = traitlets.Unicode(allow_none=True)
    object = traitlets.Tuple()

    def __init__(self, name, *object, alias=None, vars=None):
        super().__init__(name=name, object=object, alias=alias, vars=vars)

    def collect(self):
        return collect(self.name, *self.object, self.alias)

    def test(self):
        self.test_result = run(self.collect())
        return self.test_result

    def main(self, **kwargs):
        return IPython.display.Markdown(F"""```pytb\n{show(self.test()) or ""}```""")

    def description(self, object):
        self.alias = object
        return self


class TestExtension(nowidget.base.Trait):
    medial_test_definitions = traitlets.List()
    pattern = traitlets.Unicode('test_')
    visitor = traitlets.Instance('ast.NodeTransformer')

    def register(self):
        super().register()
        self.visitor.register()

    def unregister(self):
        super().unregister()
        self.visitor.unregister()

    @ traitlets.default('visitor')
    def _default_visitor(self):
        return Definitions(parent=self)

    def post_run_cell(self, result):
        if not self.enabled:
            return
        if result.error_before_exec or result.error_in_exec:
            return
        tests = []
        while self.medial_test_definitions:
            name = self.medial_test_definitions.pop(0)
            object = self.parent.user_ns.get(name, None)
            if name.startswith(self.pattern) or nowidget.util.istype(object, unittest.TestCase):
                tests.append(object)
        if tests:
            test = Test("__main__", *tests,
                        alias=F"In[{result.execution_count}]", vars=["__test__"])
            test.display()


def load_ipython_extension(shell):
    if not shell.has_trait('test_extension'):
        shell.add_traits(test_extension=traitlets.Instance(
            TestExtension, kw=dict(parent=shell)
        ))
        shell.test_extension.register()


def unload_ipython_extension(shell):
    shell.test_extension.unregister()
    ...
