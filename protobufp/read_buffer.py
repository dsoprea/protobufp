import logging

from threading import RLock
from struct import unpack


class ReadBuffer(object):
    """This class receives incoming data, and stores it in a list of extents 
    (also referred to as buffers). It allows us to leisurely pop off sequences 
    of bytes, which we build from the unconsumed extents. As the extents are 
    depleted, we maintain an index to the first available, non-empty extent. 
    We will only occasionally cleanup.
    """

    __locker = RLock()
# TODO: Reduce this for testing.
    __cleanup_interval = 100
    
    def __init__(self):
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__buffers = []
        self.__length = 0
        self.__read_buffer_index = 0
        self.__hits = 0

    def push(self, data):
        with self.__class__.__locker:
            self.__buffers.append(data)
            self.__length += len(data)

    def read_message(self):
        """Try to read a message from the buffered data. A message is defined 
        as a 32-bit integer size, followed that number of bytes. First we try
        to non-destructively read the integer. Then, we try to non-
        destructively read the remaining bytes. If both are successful, we then
        go back to remove the span from the front of the buffers.
        """

        with self.__class__.__locker:
            result = self.__passive_read(4)
            if result is None:
                return None

            (four_bytes, last_buffer_index, updates1) = result
            (length,) = unpack('>I', four_bytes)

            result = self.__passive_read(length, last_buffer_index)
            if result is None:
                return None

            (data, last_buffer_index, updates2) = result

            # If we get here, we found a message. Remove it from the buffers.

            for updates in (updates1, updates2):
                for update in updates:
                    (buffer_index, buffer_, length_consumed) = update
                    self.__buffers[buffer_index] = buffer_ if buffer_ else ''
                    self.__length -= length_consumed

            self.__read_buffer_index = last_buffer_index
            self.__hits += 1
        
            if self.__hits >= self.__class__.__cleanup_interval:
                self.__cleanup()
                self.__hits = 0

        return data

    def __passive_read(self, length, start_buffer_index=None):
        """Read the given length of bytes, or return None if we can't provide 
        [all of] them yet. When the given length is available but ends in the 
        middle of a buffer, we'll split the buffer. We do this to make it 
        simpler to continue from that point next time (it's always simpler to 
        start at the beginning of a buffer), as well as simpler to remove the
        found bytes later, if need be.
        """

        if length > self.__length:
            return None
    
        with self.__class__.__locker:
            collected = []
            need_bytes = length
            i = start_buffer_index if start_buffer_index is not None \
                                   else self.__read_buffer_index

            updates = []
            while need_bytes > 0:
                len_current_buffer = len(self.__buffers[i])
                
                if need_bytes >= len_current_buffer:
                    # We need at least as many bytes as are in the current 
                    # buffer. Consume them all.
                
                    collected.append(self.__buffers[i][:])
                    updates.append((i, [], len_current_buffer))
                    need_bytes -= len_current_buffer
                else:
                    # We need less bytes than are in the current buffer. Slice
                    # the current buffer in half, even if the data isn't going
                    # anywhere [yet].
                
                    first_half = self.__buffers[i][:need_bytes]
                    second_half = self.__buffers[i][need_bytes:]

                    self.__buffers[i] = first_half
                    self.__buffers.insert(i + 1, second_half)
                    
                    # We only mark the buffer that came from the first half as
                    # having an update (the second half of the buffer wasn't 
                    # touched).
                    collected.append(first_half)
                    updates.append((i, [], need_bytes))
                    need_bytes = 0

                i += 1

        sequence = ''.join(collected)

        return (sequence, i, updates)
    
    def __cleanup(self):
        """Clip buffers that the top of our list that have been completely 
        exhausted.
        """
# TODO: Test this.
        with self.__class__.__locker:

            while self.__read_buffer_index > 0:
                del self.__buffers[0]
                self.__read_buffer_index -= 1

