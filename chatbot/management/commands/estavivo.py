from django.core.management.base import BaseCommand
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import os

class Command(BaseCommand):
    help = 'Entrena el ChatBot con corpus conversacionales en español'

    def handle(self, *args, **options):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        DB_PATH_COMMAND = os.path.join(BASE_DIR, 'chatbot_db.sqlite3')

        chatbot_trainer_instance = ChatBot(
            'CL4P-TP',
            storage_adapter='chatterbot.storage.SQLStorageAdapter',
            database_uri=f'sqlite:///{DB_PATH_COMMAND}'
        )

        trainer = ChatterBotCorpusTrainer(chatbot_trainer_instance)

        self.stdout.write(self.style.SUCCESS('Iniciando entrenamiento del corpus en español...'))

        # Entrenar con el corpus de español (saludos, conversaciones básicas, etc.)
        trainer.train('chatterbot.corpus.spanish')
        # Puedes añadir más corpus o tus propios archivos .yml personalizados
        trainer.train('chatterbot.corpus.spanish.greetings')
        trainer.train('chatterbot.corpus.spanish.conversations')
        trainer.train('../entrenar.py')

        self.stdout.write(self.style.SUCCESS('Entrenamiento completado con éxito.'))