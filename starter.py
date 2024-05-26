import pika

STARTING_NODE = 'A'
STARTER_STRING = "STARTER"


if __name__ == '__main__':
    conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = conn.channel()

    channel.basic_publish(
        exchange='',
        routing_key=STARTING_NODE,
        body=f'T:{STARTER_STRING}'
    )
    print("Started!")
    conn.close()
