##Introduction

*Protocol Buffers* is a widely used and efficient format for expressing complex
messaging formats as byte-streams. However, even though *Protocol Buffers* gets 
you from the message object to a string, it's up to you to manage sending it on
the wire, as well as how to buffer incoming messages and detect those messages'
types.

This is the standard process for sending messages:

1. Populate message.
2. Serialize message.
3. Prepend total message length and type.
4. Send message.

This is the standard process for receiving messages:

1. Wait for enough bytes to determine length.
2. Wait for enough bytes to process whole message.
3. Remove the bytes for the message from the front of the incoming message 
   buffer.
3. Identify message class from embedded message-type.
4. Deserialize message.

*protobufp* ("Protocol Buffers Processor") extends standard Protocol Buffer 
message serialization with functionality to streamline the above steps. Though 
these steps are standard for byte communication, and are handled by code that 
exists in multiple forms and multiple places in your projects, mine, and 
everyone else's, it's a serious pain to not have a standard solution that can
be simply pulled-in as a dependency.

##Usage

The following example uses a StringIO object to act as the byte-stream (rather
than sockets, files, 0MQ, etc...). I've only included the parts of the code
necessary to describe the process.

First, we build a list of test-messages:

```python
from test_msg_pb2 import TestMsg

from protobufp.processor import Processor

def get_random_message():
    rand = lambda: randint(11111111, 99999999)

    t = TestMsg()
    t.left = rand()
    t.center = "abc"
    t.right = rand()

    return t

messages = [get_random_message() for i in xrange(5)]
```

We then create an instance of the processor and give it a list of message 
types. If new message-types will have to be added over time, it's important 
that the indices remain unchanged for the existing types.

```python
msg_types = [TestMsg]
p = Processor(msg_types)
```

Load the byte-stream with messages.

```python
s = StringIO()

for msg in messages:
    s.write(p.serializer.serialize(msg))
```

Write the data from the StringIO object to the processor. In the real-world,
you might be pushing one chunk at a time from a socket.

```python
p.push(s.getvalue())
```

Now, read one message at a time. This automatically identifies the messages,
pops them off the buffer, identifies the message-type class, and unserializes.

```python
j = 0
while 1:
    in_msg = p.read_message()
    if in_msg is None:
        break

    assert messages[j].left == in_msg.left
    assert messages[j].center == in_msg.center
    assert messages[j].right == in_msg.right

    j += 1
```

