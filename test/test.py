#!/usr/bin/env python2.7

import sys
sys.path.insert(0, '..')

from cStringIO import StringIO
from test_msg_pb2 import TestMsg
from random import randint

import log_config

from protobufp.processor import Processor

def get_random_message():
    rand = lambda: randint(11111111, 99999999)

    t = TestMsg()
    t.left = rand()
    t.center = "abc"
    t.right = rand()

    return t

messages = [get_random_message() for i in xrange(5)]

msg_types = [TestMsg]

p = Processor(msg_types)
s = StringIO()

# Build the message stream.

i = 0
for msg in messages:
    print("Pushing message (%d)." % (i))
    s.write(p.serializer.serialize(msg))

    i += 1

# Push the stream into the processor.

p.push(s.getvalue())

# Pop the newest message off the processor, one by one, until they're depleted.

j = 0
while 1:
    in_msg = p.read_message()
    if in_msg is None:
        break

    print("Read message (%d) of type [%s], and now verifying." % 
          (j, in_msg.__class__.__name__))

    assert messages[j].left == in_msg.left
    assert messages[j].center == in_msg.center
    assert messages[j].right == in_msg.right

    j += 1

