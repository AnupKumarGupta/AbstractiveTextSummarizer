"""

Usage
=====
Unescape &amp;, &lt;, and &gt; in a string of data and convert it to "and" ,"less than","greater than"

(Also unescapes UpperCase Tokens)

"""

import types
import re

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



# string_ = '''<DOC>
# <DOCNO> APW19981016.0240 </DOCNO>
# <DOCTYPE> NEWS </DOCTYPE>
# <TXTTYPE> NEWSWIRE </TXTTYPE>
# <TEXT>
# Cambodian leader Hun Sen on Friday rejected opposition parties' demands
# for talks outside the country, accusing them of trying to ``internationalize''
# the political crisis. Government and opposition parties have asked
# King Norodom Sihanouk to host a summit meeting after a series of post-election
# negotiations between the two opposition groups and Hun Sen's party
# to form a new government failed. Opposition leaders Prince Norodom
# Ranariddh and Sam Rainsy, citing Hun Sen's threats to arrest opposition
# figures after two alleged attempts on his life, said they could not
# negotiate freely in Cambodia and called for talks at Sihanouk's residence
# in Beijing. Hun Sen, however, rejected that. ``I would like to make
# it clear that all meetings related to Cambodian affairs must be conducted
# in the Kingdom of Cambodia,'' Hun Sen told reporters after a Cabinet
# meeting on Friday. ``No-one should internationalize Cambodian affairs.
# It is detrimental to the sovereignty of Cambodia,'' he said. Hun Sen's
# Cambodian People's Party won 64 of the 122 parliamentary seats in
# July's elections, short of the two-thirds majority needed to form
# a government on its own. Ranariddh and Sam Rainsy have charged that
# Hun Sen's victory in the elections was achieved through widespread
# fraud. They have demanded a thorough investigation into their election
# complaints as a precondition for their cooperation in getting the
# national assembly moving and a new government formed. Hun Sen said
# on Friday that the opposition concerns over their safety in the country
# was ``just an excuse for them to stay abroad.'' Both Ranariddh and
# Sam Rainsy have been outside the country since parliament was ceremonially
# opened on Sep. 24. Sam Rainsy and a number of opposition figures have
# been under court investigation for a grenade attack on Hun Sen's Phnom
# Penh residence on Sep. 7. Hun Sen was not home at the time of the
# attack, which was followed by a police crackdown on demonstrators
# contesting Hun Sen's election victory. The Sam Rainsy Party, in a
# statement released Friday, accused Hun Sen of being ``unwilling to
# make any compromise'' on negotiations to break the deadlock. ``A meeting
# outside Cambodia, as suggested by the opposition, could place all
# parties on more equal footing,'' said the statement. ``But the ruling
# party refuses to negotiate unless it is able to threaten its negotiating
# partners with arrest or worse.''
# </TEXT>
# </DOC>
# '''


def remove_fake_newlines(string_):

    to_be_rem =[]
    for m in re.finditer('\n', string_):
        if string_[m.start() - 1] !='.':
            to_be_rem.append(m.start())

    string_new = string_[0:to_be_rem[0]]

    for x in xrange(len(to_be_rem)-1):
        string_new += string_[to_be_rem[x]+1:to_be_rem[x+1]]+" "

    return string_new
