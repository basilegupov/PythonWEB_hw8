import pika
import json
from datetime import datetime
from mongoengine import connect, disconnect
from faker import Faker
from models import Contact


# Підключення до RabbitMQ
credentials = pika.PlainCredentials("guest", "guest")
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost", credentials=credentials))
channel = connection.channel()

# Оголошення черг
q1_name = "email"
q2_name = "sms"
channel.queue_declare(queue=q1_name)
channel.queue_declare(queue=q2_name)

# Підключення до бази даних MongoDB
connect(
    db="hw8-2dod",
    host="mongodb+srv://user71:19710822@cluster0.wvawurb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
)


def create_contacts(i: int):
    # Генерування фейкових контактів та збереження їх у базі даних
    fake = Faker()
    for _ in range(i):
        contact = Contact(
            full_name=fake.name(),
            email=fake.email(),
            phone=fake.phone_number(),
            is_sent=False,
            preferred_contact_method=fake.random_element(elements=('sms', 'email')))
        contact.save()


if __name__ == '__main__':

    create_contacts(10)

    for contact in Contact.objects():
        if contact.is_sent:
            continue
        if contact.preferred_contact_method == 'email':
            q_name = q1_name
        else:
            q_name = q2_name

        # Відправка повідомленнь у черги контактам RabbitMQ
        message = {"id": str(contact.id),
                   "payloads": f"Date:{datetime.now().isoformat()}"}
        channel.basic_publish(exchange="", routing_key=q_name, body=json.dumps(message).encode())

    print("Messages sent to queues")

    # Закриття з'єднання з RabbitMQ
    connection.close()
