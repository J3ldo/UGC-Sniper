try: from .bot import Bot
except (ModuleNotFoundError, ImportError): pass

try: from .events import *
except (ModuleNotFoundError, ImportError): pass

try: from .web import start_site
except (ModuleNotFoundError, ImportError): pass