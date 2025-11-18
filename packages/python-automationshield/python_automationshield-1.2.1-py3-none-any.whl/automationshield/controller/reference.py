class Reference:
    """Reference class. Base for :py:class:`ConstantReference`, :py:class:`PresetReference` and :py:class:`CallbackReference`. The class implements :py:meth:`__call__` to provide the *next* reference."""
    def __init__(self, ref) -> None:
        self.ref = ref

    def __call__(self, *args) -> int | float:
        return self.ref


class ConstantReference(Reference):
    """Reference class for constant reference. Provide a reference value to the constructor. Any call to :py:meth:`~ConstantReference.__call__` returns the reference."""
    pass


class PresetReference(Reference):
    """Reference class for preset reference. Provide a sequence-like reference to the constructor. \
        Every subsequent call to :py:meth:`~PresetReference.__call__` will return the *next* value in the sequence, starting at index 0.
    """
    def __init__(self, ref) -> None:
        super().__init__(ref)
        self.i = -1

    def __call__(self, *args) -> int | float:
        self.i += 1
        return self.ref[self.i]
