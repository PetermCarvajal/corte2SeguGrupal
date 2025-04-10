from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

# Crear el bot
chatbot = ChatBot(
    "CL4P-TP",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    database="db.sqlite3"  # Puedes cambiar el nombre si quieres
)

# 🔥 Borrar todo lo que ya aprendió (reiniciar el management)
chatbot.storage.drop()

