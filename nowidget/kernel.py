import IPython
import ipykernel.ipkernel
import ipykernel.kernelapp
import traitlets
import types
import ipykernel.kernelspec
import ipykernel.zmqshell
import pathlib

ORIGINAL_KERNEL = None


class pidgyKernel(ipykernel.ipkernel.IPythonKernel):
    def init_metadata(self, object):
        """capture the metadata passed from jupyterlab.
        https://github.com/jupyterlab/jupyterlab/blob/master/packages/cells/src/widget.ts#L1031
        """
        self.shell._last_parent = object
        return super(type(self), self).init_metadata(object)


def load_ipython_extension(shell):
    """patch the shell to include metadata"""
    global ORIGINAL_KERNEL
    if not ORIGINAL_KERNEL:
        if hasattr(shell, 'kernel'):
            ORIGINAL_KERNEL = type(shell.kernel)
        shell.kernel.init_metadata = types.MethodType(
            pidgyKernel.init_metadata, shell.kernel)


def unload_ipython_extension(shell):
    if ORIGINAL_KERNEL:
        shell.kernel.init_metadata = types.MethodType(
            getattr(ORIGINAL_KERNEL, 'init_metadata'), shell.kernel
        )
