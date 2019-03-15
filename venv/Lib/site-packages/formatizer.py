import inspect
import sys

PY3 = sys.version_info[0] == 3
if PY3:  # pragma: no cover
    import _string


class LiteralFormatter(object):
    def format(self, format_string, globals, locals, recursion_depth=2):
        if recursion_depth < 0:
            raise ValueError('Max string recursion exceeded')

        # Parse the format string and build the result
        result = []

        for literal_text, expression, format_spec, conversion in \
                self.parse(format_string):

            # Regular text (e.g. 'Hello there')
            if literal_text:
                result.append(literal_text)

            # An expression (e.g. '{1 + 2}')
            if expression is not None:
                obj = eval(expression, globals, locals)
                obj = self.convert_field(obj, conversion)
                format_spec = self.format(format_spec, globals, locals,
                                          recursion_depth - 1)
                result.append(format(obj, format_spec))

        return ''.join(result)

    def parse(self, format_string):
        if PY3:
            return _string.formatter_parser(format_string)  # pragma: no cover
        else:
            return format_string._formatter_parser()  # pragma: no cover

    def convert_field(self, value, conversion):
        if conversion is None:
            return value
        elif conversion == 's':
            return str(value)
        elif conversion == 'r':
            return repr(value)
        raise ValueError(
            "Unknown conversion specifier {0!s}".format(conversion)
        )


def f(format_string):
    caller_frame = inspect.currentframe().f_back
    caller_globals = caller_frame.f_globals
    caller_locals = caller_frame.f_locals
    lf = LiteralFormatter()
    return lf.format(format_string, caller_globals, caller_locals)
