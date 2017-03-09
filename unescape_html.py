"""

Usage
=====
Unescape &amp;, &lt;, and &gt; in a string of data and convert it to "and" ,"less than","greater than"

(Also unescapes UpperCase Tokens)

"""

import types

try:
    _StringTypes = [types.StringType, types.UnicodeType]
except AttributeError:
    _StringTypes = [types.StringType]

"""

Usage
=====

Replace substrings of a string using a dictionary.

Parameters
==========

string_  : The string
dict     : The dictionary used to replace key(substrings in string_) by its values(new substrings)

Returns
=======

Modified string data

Examples
========
print unescape_html.__dict_replace("String :: Hello I am new",{"Hello":"Hi","new":"changed"})

String :: Hi I am changed

"""


def __dict_replace(string_, dict):
    for key, value in dict.items():
        string_ = string_.replace(key, value)
    return string_


"""

Usage
=====

Unescape &amp;, &lt;, and &gt; in a string of data.

Parameters
==========

data :     The string to unescaped
entities : You can unescape other strings of data by passing a dictionary as
           the optional entities parameter.  The keys and values must all be
           strings

Returns
=======

Unescaped string data

Examples
========
print unescape_html.unescape("Unescapes :: &amp; , &AMP; , &lt; , &gt;")

Unescapes :: and , and , less than , greater than

"""


def unescape(data, entities={}):
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
