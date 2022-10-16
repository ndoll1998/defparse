from typing import _type_check, _SpecialForm, _GenericAlias

@_SpecialForm
def Ignore(self, parameter):
    """ Type Modifier to mark an argument as ignore.

        Arguments with types marked by `Ignore` are not added
        to the argument parser.
    """
    # check type
    arg = _type_check(parameter, msg=f"{self} requires a single type.")
    return _GenericAlias(self, (arg,))
