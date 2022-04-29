"""
    Author Zotov Nikita
"""
from server.frontend.configurator import Configurator
from server.frontend.routes import app
from server.server import Server


def main():
    try:
        configurator = Configurator()
        server = Server(app)
        server.start(configurator)
    except OSError as error:
        print(error)


if __name__ == '__main__':
    main()
