from protobufp.serializer import Serializer
from protobufp.read_buffer import ReadBuffer


class Processor(object):
    """Automatically identify and unserialize messages.
    
    mapping is a dictionary of INTs to message classes.
    """

    def __init__(self, mapping):
        self.__mapping = mapping
        self.__rb = ReadBuffer()

    def push(self, data):
        self.__rb.push(data)

    def read_message(self):
        data = self.__rb.read_message()
        if data is not None:
            return self.serializer.unserialize(data)

    @property
    def serializer(self):
        try:
            return self.__serializer
        except AttributeError:
            self.__serializer = Serializer(self)
            return self.__serializer

    @property
    def mapping(self):
        return self.__mapping

