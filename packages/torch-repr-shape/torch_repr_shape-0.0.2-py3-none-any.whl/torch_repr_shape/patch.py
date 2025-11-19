import builtins
import os
import sys


def enable_torch_repr_shape():
    """
    Enable torch.Tensor.__repr__ to print patches for shape.

    Satisfy:
    -Lazy loading: If torch has not been imported yet, the patch will be applied until the first import of torch.
    -Idempotent: repeated calls will not repeat the patch
    -Can be disabled with one click: set the environment variable DISABLE_TORCH_REPR_SHAPE=1 to disable it
    """
    # One click to close

    if os.environ.get("DISABLE_TORCH_REPR_SHAPE") == "1":
        return

    # If torch is already in sys.modules, just patch it directly

    if "torch" in sys.modules:
        _patch()
        return

    # Otherwise, hook import, wait for the first import torch and then patch

    orig_import = builtins.__import__

    def _import(name, *args, **kwargs):
        m = orig_import(name, *args, **kwargs)
        if name == "torch":
            try:
                _patch()
            finally:
                # Make sure to restore the original import to avoid affecting other modules

                builtins.__import__ = orig_import
        return m

    builtins.__import__ = _import


def _patch():
    try:
        import torch

        T = torch.Tensor
        # already patched it so do not repeat it again.

        if getattr(T, "__repr__adds_shape__", False):
            return

        orig = T.__repr__

        def _new(self):
            try:
                return f"{{Tensor:{tuple(self.shape)}}} " + orig(self)
            except Exception:
                return orig(self)

        T.__repr__ = _new
        T.__repr__adds_shape__ = True
    except Exception:  # noqa: S110
        # Does not affect normal operation

        pass
