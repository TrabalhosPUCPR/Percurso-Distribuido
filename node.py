from sys import argv
from pika import BlockingConnection, ConnectionParameters
from enum import Enum
from starter import STARTER_STRING


class States(Enum):
    STARTER = 0
    SLEEPING = 1
    VISITED = 2
    OK = 3


if len(argv) < 2:
    print("Invalid")
    exit(-1)

conn = BlockingConnection(ConnectionParameters('localhost'))
channel = conn.channel()
identifier = argv[1]
neighbours = argv[2:]

channel.queue_declare(queue=identifier, auto_delete=True)
for v in neighbours:
    channel.queue_declare(queue=v, auto_delete=True)

state = States.SLEEPING
not_visited = []
first_origin = ""
starter = False


def spontaneous():
    global starter, not_visited, neighbours
    print("Node is now the initiating node!")
    starter = True
    not_visited = neighbours[:]
    visited()


def visited():
    global not_visited, state, starter, first_origin
    if len(not_visited) == 0:
        state = States.OK
        if not starter:
            send_data('R', first_origin)
    else:
        state = States.VISITED
        next_node = not_visited.pop(0)
        send_data('T', next_node)


def send_data(data: str, destination: str):
    global identifier, channel
    channel.basic_publish(
        exchange='',
        routing_key=destination,
        body=f"{data}:{identifier}"
    )


def receive(origin, data):
    global state, first_origin, not_visited
    try:
        print(f"Received message {data} from origin {origin}")
        if origin == STARTER_STRING:
            spontaneous()
            return "Successfully started"
        elif data == 'T':
            if state == States.SLEEPING:
                first_origin = origin
                not_visited = neighbours[:]
                not_visited.remove(origin)
                visited()
            elif state == States.VISITED:
                not_visited.remove(origin)
                send_data('B', origin)
        elif state == States.VISITED:
            visited()
    except Exception as e:
        print(f"An exception occured: {e}")


def callback(_conn, _deliver, _properties, bytes):
    message = bytes.decode()
    print(f"Message {message} received")
    m = message.split(":")
    if len(m) < 2:
        print("Invalid message")
    else:
        if m[1] == STARTER_STRING:
            spontaneous()
        else:
            receive(m[1], m[0])


channel.basic_consume(
    queue=identifier,
    on_message_callback=callback,
    auto_ack=True
)

try:
    print(f"Node {identifier} active with neighbours {neighbours}!")
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()

conn.close()
