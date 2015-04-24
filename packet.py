from pyparsing import *
import re
import pprint
import struct

class I3Packet:
    # First we have the decoding part, to turn a packet string into a python array

    i3_packet_bnf = """
    map
        ([ members ])
        ([ ])
    array
        ({ elements })
        ({ })
    members
        string : value
        members , string : value
    elements
        value
        elements , value
    value 
        string
        number
        array
        map
    """

    def unescapeString(s,l,toks):
        n = toks[0]
        n = n.replace('\\"', '"')
        n = n.replace('\\\\', '\\')
        n = n.replace('\\r', '\r')
        n = n.replace('\\n', '\n')
        n = n[1:-1]
        return n


    def convertNumbers(s,l,toks):
        n = toks[0]
        try:
            return int(n)
        except ValueError:
            return float(n)
            

    i3String = dblQuotedString.setParseAction( unescapeString )
    i3Number = Combine( Optional('-') + ( '0' | Word('123456789',nums) ) +
                        Optional( '.' + Word(nums) ) +
                        Optional( Word('eE',exact=1) + Word(nums+'+-',nums) ) )
    i3Number.setParseAction( convertNumbers )

    i3Map = Forward()
    i3Value = Forward()
    i3Elements = delimitedList( i3Value )
    i3Array = Group(Suppress('({') + Optional(i3Elements) + Suppress('})') )

    i3Value << ( i3String | i3Number | Group(i3Map)  | i3Array )
    memberDef = Group( i3String + Suppress(':') + i3Value )
    i3Members = delimitedList( memberDef )
    i3Map << Dict( Suppress('([') + Optional(i3Members) + Suppress('])') )

    # Then we have the encoding part, to turn a python array into a packet string

    def escapeString(s):
        n = s.replace('\\', '\\\\')
        n = n.replace('"', '\\"')
        n = n.replace('\r', '\\r"')
        n = n.replace('\n', '\\n"')
        n = '"' + n + '"'
        return n

    def _encode(data):
        if str(type(data)) == "<class 'list'>":
            x = []
            for k in data:
                x.append(I3Packet._encode(k))
            n = '({' + ','.join(x) + '})'
            return n
        elif str(type(data)) == 'Dict':
            x = dict()
            for k, v in data:
                a = I3Packet._encode(k)
                b = I3Packet._encode(v)
                x[a] = b
            n = '([' + ','.join(x) + '])'
            return n
        elif str(type(data)) == "<class 'str'>":
            return I3Packet.escapeString(data)
        else:
            return str(data)

    def encode(data):
        if str(type(data)) != "<class 'list'>":
            raise TypeError('Data must be passed in as an array, not %r', type(data))
        return I3Packet._encode(data)

    def mudmode(text: str):
        raw_bytes = bytes(text, 'cp1252')
        raw_bytelen = len(raw_bytes) + 4
        bytestream = struct.pack('!L', raw_bytelen) + raw_bytes
        return bytestream


    # And finally the class functions to let us use all this easily

    def __init__(self, text: str=None, data=None):
        if text is not None:
            self._text = text
            self._bytestream = I3Packet.mudmode(self._text)

        if data is not None:
            if str(type(data)) != "<class 'list'>":
                raise TypeError('Data must be passed in as an array, not %r', type(data))
            self._data = data

    @property
    def text(self):
        if self._text is None:
            self._text = I3Packet.encode(self._data)
            self._bytestream = I3Packet.mudmode(self._text)
        return self._text

    @text.setter
    def text(self, text: str):
        self._text = text
        self._bytestream = I3Packet.mudmode(self._text)
        self._data =  I3Packet.i3Value.parseString(self._text)[0]

    @property
    def data(self):
        if self._data is None:
            self._data =  I3Packet.i3Value.parseString(self._text)[0]
            self._bytestream = I3Packet.mudmode(self._text)
        return self._data

    @data.setter
    def data(self, data):
        if str(type(data)) != "<class 'list'>":
            raise TypeError('Data must be passed in as an array, not %r', type(data))
        if len(data) < 6:
            raise ValueError('Packets require at least 6 elements, not %d', len(data))
        self._data = data
        self._text = I3Packet.encode(self._data)
        self._bytestream = I3Packet.mudmode(self._text)

    @property
    def bytestream(self):
        if self._text is None:
            self._text = I3Packet.encode(self._data)
            self._bytestream = I3Packet.mudmode(self._text)
        return self._bytestream


if __name__ == '__main__':
    testdata = """
    ({ "channel-m", 5, "Bloodlines", "quixadhal", 0, 0, "imud_gossip", "Quixadhal", "I probably have to deal with \\"quotes\\" and don't have all the escapes in place yet." })
    """
    testob = [ "channel-m", 5, "Bloodlines", "quixadhal", 0, 0, "imud_gossip", "Quixadhal", "I probably have to deal with \"quotes\" and don't have all the escapes in place yet." ]

    print("Raw String:")
    pprint.pprint( testdata )

    packet = I3Packet()
    packet.text = testdata
    print("Decoded:")
    pprint.pprint( packet.data.asList() )

    def testPrint(x):
        print(type(x),repr(x))

    print("Raw Data:")
    pprint.pprint( testob )

    packet.data = testob
    print("Encoded:")
    pprint.pprint( packet.text )
    print("Mudmode:")
    pprint.pprint( packet.bytestream )

