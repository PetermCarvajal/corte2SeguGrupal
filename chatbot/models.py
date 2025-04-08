from django.db import models

class ChatbotQuery(models.Model):
    query = models.CharField(max_length=1000)
    processed_query = models.TextField(blank=True)  # Este campo debe existir
    relevant_docs = models.TextField(blank=True) # Historial
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    intent = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'consulta chatbot'
        verbose_name_plural = 'consultas chatbot'

    def __str__(self):
        return self.query