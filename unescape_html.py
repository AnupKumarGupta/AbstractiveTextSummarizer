import types

try:
    _StringTypes = [types.StringType, types.UnicodeType]
except AttributeError:
    _StringTypes = [types.StringType]


def __dict_replace(s, d):
    """Replace substrings of a string using a dictionary."""
    for key, value in d.items():
        s = s.replace(key, value)
    return s


def unescape(data, entities={}):
    """Unescape &amp;, &lt;, and &gt; in a string of data.

    You can unescape other strings of data by passing a dictionary as
    the optional entities parameter.  The keys and values must all be
    strings; each key will be replaced with its corresponding value.
    """
    data = data.replace("&lt;", "less than")
    data = data.replace("&LT;", "less than")
    data = data.replace("&gt;", "greater than")
    data = data.replace("&GT;", "greater than")

    if entities:
        data = __dict_replace(data, entities)
    # must do ampersand last
    data = data.replace("&AMP;", "and")
    data = data.replace("&amp;", "and")
    return data
