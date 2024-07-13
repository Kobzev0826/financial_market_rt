from .injector import Injector

injector = Injector()
register = injector.register
inject = injector.inject

__version__ = "1.2.0"
