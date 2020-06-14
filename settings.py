class _Option:
    def __init__(self, /, validator = None, initValue = None, required = False):
        if required and initValue is None:
            raise ValueError('required option should have initial value')

        if (validator is not None) and (initValue is not None) and (validator(initValue) is False):
            raise ValueError('initial value should be valid')

        self.validator = validator
        self.initValue = initValue
        self.required = required
        self.value = None

def _typeCheck(decltype):
    return lambda o: isinstance(o, decltype)

_optionMap = {
    # string options
    'username': _Option(validator=_typeCheck(str), initValue='YOUR_USERNAME_HERE', required=True),
    'password': _Option(validator=_typeCheck(str), initValue='YOUR_PASSWORD_HERE', required=True),
    'tags':     _Option(validator=_typeCheck(str), initValue='LastOrigin r-18', required=True),

    # int options
    'max-page-image-count': _Option(validator=_typeCheck(int), initValue=0, required=True),
}
