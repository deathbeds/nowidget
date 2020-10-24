# `nowidget`

`nowidget` is a pure-python suite of interactive widgets based off of `traitlets` that do not explicitly require an javascript extensions. 


        import nowidget

probably the most useful `nowidget` object is `nowidget.Template`, it is  `jinja2` display objects using `IPython`'s rich display. `nowidget.Template` is interactive and updates on cell exection or widget events. for example, in a notebook, the `nowidget.Template` will automatically discover the value of `cookies`.

        cookies = 3
        nowidget.Template("When you eat {{cookies}} cookies, you consume {{cookies*50}} calories.")

`nowidget.Template` will update when a cell is run. in the example above, if `cookie` were changed in a later cell then template will update. updating can be disabled with the `enabled` flag.

        nowidget.Template("When you eat {{cookies}} cookies, you consume {{cookies*50}} calories.",
                          enabled=True
        )

the `nowidget` extension adds some new traits to `IPython`'s interactive shell:

```ipython
%load_ext nowidget
```


1. `shell.test` is a primary default feature of the `nowidget` extension.

    it provides formal `doctest and unittest`sto be executed with each cell execution. as an example.

        def test_me():

    function being with `"test_*"` are executed as tests.

        shell = __import__("IPython").get_ipython()
        if shell:

1. `shell.display_manager` manages updating `IPython` display objects when shell events occur.

3. `shell.trace` uses `monkeytype` to generate type stubs from the interactive computing experience.

    turn tracing on and off with

            shell.trace.on()
            shell.trace.off()

    or as a context manager

            with shell.trace:
                ...

## developer tasks

a suite of tasks based off of `doit`.

        def task_book():

build the docs using jupyter book.

            return dict(actions=["jb build ."], file_dep=['_toc.yml'], targets=['_build/html'])

        def task_pdf():

export a pdf version of the docs.

            return dict(actions=["jb build . --builder pdfhtml"], file_dep=['_toc.yml'], targets=['_build/pdf/book.pdf'])
