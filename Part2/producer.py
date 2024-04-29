import pika
import json
from datetime import datetime
from mongoengine import connect, disconnect
from faker import Faker
from models import Contact

# Отключаемся от существующего соединения MongoEngine, если оно уже установлено
disconnect()

# Підключення до RabbitMQ
credentials = pika.PlainCredentials("guest", "guest")
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost", credentials=credentials))
channel = connection.channel()

# Оголошення черги
q_name = "email"
channel.queue_declare(queue=q_name)

# Підключення до бази даних MongoDB
connect(
    db="hw8-2",
    host="mongodb+srv://user71:19710822@cluster0.wvawurb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
)


def create_contacts(i: int):
    # Генерування фейкових контактів та збереження їх у базі даних
    fake = Faker()
    for _ in range(i):
        contact = Contact(
            full_name=fake.name(),
            email=fake.email(),
            is_sent=False
        )
        contact.save()

        # Відправка повідомлення у чергу RabbitMQ
        message = {"id": str(contact.id),
                   "payloads": f"Date:{datetime.now().isoformat()}"}
        channel.basic_publish(exchange="", routing_key=q_name, body=json.dumps(message).encode())

    print("Messages sent to queue")

    # Закриття з'єднання з RabbitMQ
    connection.close()


if __name__ == '__main__':
    create_contacts(5)
