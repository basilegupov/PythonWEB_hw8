from mongoengine import connect, Document, StringField, BooleanField

# Підключення до бази даних MongoDB
connect(
    db="hw8-2dod",
    host="mongodb+srv://user71:19710822@cluster0.wvawurb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
)


# Визначення моделі Contact
class Contact(Document):
    full_name = StringField(required=True)
    email = StringField(required=True)
    phone = StringField(required=True)
    is_sent = BooleanField(default=False)
    preferred_contact_method = StringField(choices=('sms', 'email'), default='email')
