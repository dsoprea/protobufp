import logging

from struct import pack, unpack
from cStringIO import StringIO


class Serializer(object):
    def __init__(self, processor):
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__processor = processor
        self.__mapping = processor.mapping

        self.__mapping_r = dict([(v.__name__, k) 
                                 for (k, v) 
                                 in self.__mapping.iteritems()])

    def serialize(self, o):
        type_ = self.__mapping_r[o.__class__.__name__]
        type_string = pack('!I', type_)

        serialized = o.SerializeToString()

        s = StringIO()
        s.write(pack('!I', 4 + len(serialized)))
        s.write(type_string)
        s.write(serialized)

        return s.getvalue()

    def unserialize(self, serialized):
        self.__log.debug("Unserializing (%d) bytes." % (len(serialized)))
        (type_,) = unpack('!I', serialized[:4])

        o = self.__mapping[type_]()
        o.ParseFromString(serialized[4:])

        return o

