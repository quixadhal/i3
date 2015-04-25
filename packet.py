from pyparsing import *
import pprint
import struct


def unescape_string(s, l, toks):
    """
    Remove outer quotes and unescape special characters from I3.
    :param s: passed in from callback
    :param l: passed in from callback
    :param toks: token to be modified
    :return: modified string from token
    """
    n = toks[0]
    n = n.replace('\\"', '"')
    n = n.replace('\\r', '\r')
    n = n.replace('\\n', '\n')
    n = n.replace('\\x00', '\x00')
    n = n.replace('\\\\', '\\')
    n = n[1:-1]
    return n


def escape_string(s):
    """
    Escapes special characters and adds quotes for I3.
    :param s: string to be processed
    :return: modified string for I3 consumption
    """
    n = s.replace('\\', '\\\\')
    n = n.replace('"', '\\"')
    n = n.replace('\r', '\\r"')
    n = n.replace('\n', '\\n"')
    n = n.replace('\x00', '\\x00"')
    n = '"' + n + '"'
    return n


def from_i3number(s, l, toks):
    """
    Convert an I3 "number" to an int or float for python.
    :param s: passed in from callback
    :param l: passed in from callback
    :param toks: token to be modified
    :return: numeric type from token
    """
    n = toks[0]
    try:
        return int(n)
    except ValueError:
        return float(n)


class I3Packet:
    """
    This class encapsulates the basic encoding and decoding of I3 packet strings.

    To decode a packet, simply initialize a class instance with the extracted text,
    or assign it via the text parameter.  The data member will be an array containing
    the extracted elements.

    To encode a data chunk for I3 trasmission, simply pass the array of elements in to
    the initializer, or assign via the data parameter.  The text member will contain the
    text to be sent.  The mudmode member will contain a byte-encoded version with the
    leading binary length data for a "mudmode" socket.

    If you just need the mudmode encoding of a preformatted string, just assign as with the
    decode operation and use the mudmode method to get it.

    Decoding was implemented using pyparsing for simplicity.  Encoding is a simple recursion.

    NOTE: Only simple data types are handled.  Attempting to pass in an object will fail
    unless the object has a proper __repr__ method to return a string form of itself.
    """
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

    i3String = dblQuotedString.setParseAction(unescape_string)
    i3Number = Combine(Optional('-') + ( '0' | Word('123456789', nums) ) +
                       Optional('.' + Word(nums)) +
                       Optional(Word('eE', exact=1) + Word(nums + '+-', nums)))
    i3Number.setParseAction(from_i3number)

    i3Map = Forward()
    i3Value = Forward()
    i3Elements = delimitedList(i3Value)
    i3Array = Group(Suppress('({') + Optional(i3Elements) + Suppress('})'))

    i3Value << ( i3String | i3Number | Group(i3Map) | i3Array )
    memberDef = Group(i3String + Suppress(':') + i3Value)
    i3Members = delimitedList(memberDef)
    i3Map << Dict(Suppress('([') + Optional(i3Members) + Suppress('])'))

    @classmethod
    def _encode(cls, data):
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
            return escape_string(data)
        else:
            return str(data)

    @classmethod
    def encode(cls, data):
        if str(type(data)) != "<class 'list'>":
            raise TypeError('Data must be passed in as an array, not %r', type(data))
        return I3Packet._encode(data)

    @classmethod
    def mudmode(cls, text: str):
        raw_bytes = bytes(text, 'cp1252') + struct.pack('!B', 0)
        raw_bytelen = len(raw_bytes)
        bytestream = struct.pack('!L', raw_bytelen) + raw_bytes
        return bytestream

    @classmethod
    def validate_data(cls, data):
        if str(type(data)) != "<class 'list'>":
            raise TypeError('Data must be passed in as an array, not %r', type(data))
        if len(data) < 6:
            raise ValueError('Packets require at least 6 elements, not %d', len(data))
        if str(type(data[0])) != "<class 'str'>":
            raise TypeError('Element 0 must be a packet type string, not %r', type(data[0]))
        data[1] = 5
        if str(type(data[2])) not in ("<class 'str'>", "<class 'int'>"):
            raise TypeError('Element 2 must be the mud name string or 0, not %r', type(data[2]))
        if str(type(data[3])) not in ("<class 'str'>", "<class 'int'>"):
            raise TypeError('Element 3 must be the user name string or 0, not %r', type(data[3]))
        if str(type(data[4])) not in ("<class 'str'>", "<class 'int'>"):
            raise TypeError('Element 4 must be the target name string or 0, not %r', type(data[4]))
        return data

    def __init__(self, text: str=None, data=None):
        if text is not None:
            self._text = text
            self._bytestream = I3Packet.mudmode(self._text)

        if data is not None:
            self._data = I3Packet.validate_data(data)

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
        self._data = I3Packet.i3Value.parseString(self._text)[0]

    @property
    def data(self):
        if self._data is None:
            self._data = I3Packet.i3Value.parseString(self._text)[0]
            self._bytestream = I3Packet.mudmode(self._text)
        return self._data

    @data.setter
    def data(self, data):
        self._data = I3Packet.validate_data(data)
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
    testob = ["channel-m", 5, "Bloodlines", "quixadhal", 0, 0, "imud_gossip", "Quixadhal",
              "I probably have to deal with \"quotes\" and don't have all the escapes in place yet."]

    print("Raw String:")
    pprint.pprint(testdata)

    packet = I3Packet()
    packet.text = testdata
    print("Decoded:")
    pprint.pprint(packet.data.asList())

    def testPrint(x):
        print(type(x), repr(x))

    print("Raw Data:")
    pprint.pprint(testob)

    packet.data = testob
    print("Encoded:")
    pprint.pprint(packet.text)
    print("Mudmode:")
    pprint.pprint(packet.bytestream)
