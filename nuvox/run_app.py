from nuvox.config.config import Config
from nuvox.controller import Controller


if __name__ == '__main__':

    controller = Controller(config=Config())
    controller.run_app()