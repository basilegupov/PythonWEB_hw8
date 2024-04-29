import pika
from models import Contact
import json


def send_mess(phone, payloads):
    print(f"Message '{payloads}' sent to {phone}")
    return True


def main():
    # Підключення до RabbitMQ
    credentials = pika.PlainCredentials("guest", "guest")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost", credentials=credentials))
    channel = connection.channel()

    # Оголошення черги
    q_name = "sms"
    channel.queue_declare(queue=q_name)
    # Функція обробки отриманих повідомлень

    def callback(ch, method, properties, body):
        message = json.loads(body.decode())
        contact_id = message.get("id")

        if contact_id:
            try:
                # Знайти контакт у базі даних за його id
                contact = Contact.objects.get(id=contact_id)

                # Оновлення значення поля message_sent
                contact.is_sent = send_mess(contact.phone, message.get("payloads"))
                contact.save()

            except Contact.DoesNotExist:
                print(f"Contact with id {contact_id} not found.")
        else:
            print("Invalid message format.")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # Підписка на чергу та встановлення функції зворотного виклику
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=q_name, on_message_callback=callback)

    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == '__main__':
    main()
