import logging

from struct import pack, unpack
from cStringIO import StringIO


class Serializer(object):
    def __init__(self, processor):
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__p = processor
        self.__msg_types = self.__p.msg_types

        msg_types_r = {}
        i = 0
        for cls in self.__msg_types:
            msg_types_r[cls.__name__] = i
            i += 1

        self.__msg_types_r = msg_types_r

    def serialize(self, o):
        type_ = self.__msg_types_r[o.__class__.__name__]
        type_string = pack('!I', type_)

        serialized = o.SerializeToString()

        s = StringIO()
        s.write(pack('!I', 4 + len(serialized)))
        s.write(type_string)
        s.write(serialized)

        return s.getvalue()

    def unserialize(self, serialized):
        (type_,) = unpack('!I', serialized[:4])

        o = self.__msg_types[type_]()
        o.ParseFromString(serialized[4:])

        return o

