from os import environ 

class Config:
    API_ID = environ.get("API_ID", "20346550")
    API_HASH = environ.get("API_HASH", "bc79c3bea7a626887bdc0871eecf0327")
    BOT_TOKEN = environ.get("BOT_TOKEN", "8430027432:AAFe9nGLXFsIIHfLU2fXzedKg5ce2CObxkY") 
    BOT_SESSION = environ.get("BOT_SESSION", "bot") 
    DATABASE_URI = environ.get("DATABASE", "mongodb+srv://chhjgjkkjhkjhkjh@cluster0.xowzpr4.mongodb.net/")
    DATABASE_NAME = environ.get("DATABASE_NAME", "forward-bot")
    BOT_OWNER_ID = [int(id) for id in environ.get("BOT_OWNER_ID", '8252041740').split()]

class temp(object): 
    lock = {}
    CANCEL = {}
    forwardings = 0
    BANNED_USERS = []
    IS_FRWD_CHAT = []
    
