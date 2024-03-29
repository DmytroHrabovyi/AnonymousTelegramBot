from events import Events


class ConnectionManager:
    def __init__(self):
        self.users = list()
        self.events = Events()
        self.__connections = list()

    def is_empty(self):
        return self.users == []

    def enqueue(self, user):
        if not self.is_empty():
            self.create_connection([self.dequeue(), user])
        else:
            self.users.insert(0, user)

    def dequeue(self):
        return self.users.pop()

    def remove_from_queue(self, item):
        if self.is_empty() or item not in self.users:
            return

        self.users.remove(item)

    def create_connection(self, users: list):
        connection = Connection(users)
        self.__connections.append(connection)
        # Івент - список функцій (які підписані на нього)
        # Передаємо connection усім функціям які підписані на івент connection_created
        self.events.connection_created(connection)

        return connection

    def get_connection(self, user):
        for connection in self.__connections:
            if user in connection.users:
                return connection

        return None

    def disconnect_user(self, user):
        connection = self.get_connection(user)
        if connection is None:
            return False

        connection.users.remove(user)
        self.events.user_disconnected(user, connection)

        if len(connection.users) < 2:
            self.destroy_connection(connection)

    def destroy_connection(self, connection):
        self.__connections.remove(connection)
        self.events.connection_destroyed(connection)


class Connection:
    def __init__(self, users: list):
        self.users = users
