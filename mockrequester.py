from kombu import Connection, Exchange, Queue, Producer

def main():
    with Connection('amqp://guest:guest@localhost:5672//') as connection:
        grading_exchange = Exchange("grading")
        producer = Producer(connection, grading_exchange)
        for i in range(500):
            producer.publish("Hello world {0}!".format(i),
                             exchange=grading_exchange,
                             routing_key="agenttest")

if __name__ == '__main__':
    main()
