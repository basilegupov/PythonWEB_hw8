import redis
from models import Author, Quote

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


def search_quotes(command):
    # Перевірка, чи команда є в Redis
    cached_result = redis_client.get(command)
    if cached_result:
        print("Результат отримано з кешу Redis:")
        print(cached_result.decode('utf-8'))
        return
    
    if command.startswith("name:"):
        # Отримання повного імені автора
        author_name = command.split(":")[1].strip()
        if len(author_name) < 3:
            # Для скороченого запису
            author_name = f"{author_name}.*"
        quotes = Author.objects(fullname__iregex=author_name)
    elif command.startswith("tag:"):
        # Отримання тега
        tag = command.split(":")[1].strip()
        if len(tag) < 3:
            # Для скороченого запису
            tag = f"{tag}.*"
        quotes = Quote.objects(tags__iregex=tag)
    else:
        print("Невідома команда")
        return
    
    # Отримання результату та його збереження в Redis
    result = [quote.to_json() for quote in quotes]
    redis_client.set(command, '\n'.join(result))
    
    # Виведення результату
    for quote in result:
        print(quote)


if __name__ == "__main__":
    while True:
        command = input("Введіть команду: ")
        if command == "exit":
            break
        search_quotes(command)
