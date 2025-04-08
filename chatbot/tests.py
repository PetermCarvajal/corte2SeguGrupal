#from django.http import JsonResponse
#from django.views.decorators.csrf import csrf_exempt
#from . import nplutils
#from chatterbot import ChatBot
#from chatterbot.trainers import ChatterBotCorpusTrainer
#import json
## Crear o cargar el chatbot
#chatbot = ChatBot('CL4P-TP', logic_adapters=[
#    'chatterbot.logic.BestMatch'
#])
#
## Entrenarlo (solo una vez, podrías mover esto fuera de views.py luego)
#trainer = ChatterBotCorpusTrainer(chatbot)
#trainer.train("chatterbot.corpus.spanish")
#
## Vocabulario para respuestas personalizadas
#SALUDOS = ['hola', 'oe', 'hey', 'saludos', 'buenos días', 'buenos dias', 'buenas tardes', 'buenas noches',
#           'we', 'wenas', 'wey', 'ey', 'buenas', 'que tal', 'qué tal', 'alo', 'que hay', 'como estamos', 'como andamos']
#
#DESPEDIDAS = ['adios', 'chao', 'cuidate', 'hasta luego', 'hasta la proxima', 'adiós', 'nos vemos', 'chau',
#              'arrivederchi', 'nos vemos', 'chiao']
#
#AYUDA = ['ayuda', 'ayudame', 'como funciona', 'que haces']
#
#@csrf_exempt
#def chatbot_query(request):
#    if request.method == 'POST':
#        try:
#            data = json.loads(request.body)
#            query = data.get('query', '').strip().lower()
#            query_corregida = nplutils.corregir_con_regex(query, nplutils.correcciones)
#
#            if not query_corregida:
#                return JsonResponse({
#                    'success': False,
#                    'error': 'Consulta vacía.'
#                })
#
#            # Respuestas personalizadas
#            if any(saludo in query_corregida for saludo in SALUDOS):
#                return JsonResponse({
#                    'success': True,
#                    'response': "¡Hola! Soy el asistente virtual de TecLegacy. Puedes llamarme CL4P-TP 🤖. ¿En qué puedo ayudarte hoy?",
#                })
#
#            if any(despedida in query_corregida for despedida in DESPEDIDAS):
#                return JsonResponse({
#                    'success': True,
#                    'response': "¡Hasta luego! Gracias por visitar TecLegacy 💻. ¡Que tengas un excelente día!",
#                })
#
#            if any(ayuda in query_corregida for ayuda in AYUDA):
#                return JsonResponse({
#                    'success': True,
#                    'response': "Puedo ayudarte a encontrar productos en nuestra tienda. Prueba preguntándome por productos como 'muéstrame teclados gaming' o 'busco un monitor de 27 pulgadas'."
#                })
#
#            # Usar ChatterBot para respuesta general
#
#            response = chatbot.get_response(query_corregida)
#
#            return JsonResponse({
#                'success': True,
#                'response': str(response)
#            })
#
#        except Exception as e:
#            return JsonResponse({
#                'success': False,
#                'error': f'Ha ocurrido un error: {str(e)}'
#            })
#
#    return JsonResponse({
#        'success': False,
#        'error': 'Método no permitido'
#    })


#from django.http import JsonResponse
#from django.views.decorators.csrf import csrf_exempt
#from products.models import Product, Category
#from .models import ChatbotQuery
#from django.http import JsonResponse
#from django.views.decorators.csrf import csrf_exempt
#import json
#from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
#import json
#import re
#from django.db import models
#from django.http import JsonResponse
#from django.views.decorators.csrf import csrf_exempt
#import json
#
## Cargar modelo y tokenizer de Hugging Face (una vez al inicio)
#tokenizer = AutoTokenizer.from_pretrained("facebook/blenderbot-400M-distill")
#model = AutoModelForSeq2SeqLM.from_pretrained("facebook/blenderbot-400M-distill")
#
#@csrf_exempt
#def chatbot_query(request):
#    if request.method == 'POST':
#        try:
#            data = json.loads(request.body)
#            user_query = data.get('query', '').strip().lower()
#
#            if not user_query:
#                return JsonResponse({
#                    'success': False,
#                    'error': 'Consulta vacía.'
#                })
#
#            # Mensajes predefinidos de saludo
#            SALUDOS = ['hola', 'oe', 'hey', 'saludos', 'buenos días', 'buenos dias', 'buenas tardes', 'buenas noches',
#                       'we', 'wenas', 'wey', 'hey', 'ey', 'buenas', 'que tal', 'qué tal', 'alo', 'saludos', 'que hay',
#                       'como estamos', 'como andamos']
#
#            DESPEDIDAS = ['adios', 'chao', 'cuidate', 'hasta luego', 'hasta la proxima', 'adiós', 'nos vemos', 'chau',
#                          'arrivederchi', 'gracie', 'nos vemos', 'chiao']
#
#            AYUDA = ['ayuda', 'ayudame', 'como funciona', 'que haces']
#
#            # Saludo
#            if any(saludo in query for saludo in SALUDOS):
#                return JsonResponse({
#                    'success': True,
#                    'response': "¡Hola! Soy el asistente virtual de TecLegacy Puedes Llamarme CL4P-TP🤖. ¿En qué puedo ayudarte hoy?",
#                })
#
#            # Despedida
#            if any(despedida in query for despedida in DESPEDIDAS):
#                return JsonResponse({
#                    'success': True,
#                    'response': "¡Hasta luego! Gracias por visitar TecLegacy 💻. ¡Que tengas un excelente día!",
#                })
#
#            if any(ayuda in query for ayuda in AYUDA):
#                return JsonResponse({
#                    'success': True,
#                    'response': "Puedo ayudarte a encontrar productos en nuestra tienda. Prueba preguntándome por productos específicos como 'muéstrame teclados gaming' o 'busco un monitor de 27 pulgadas'. También puedes indicarme un rango de precio como 'monitores por menos de 500'."
#                })
#
#            # Procesar con el modelo de lenguaje
#            inputs = tokenizer(user_query, return_tensors="pt")
#            reply_ids = model.generate(**inputs, max_new_tokens=100)
#            response = tokenizer.decode(reply_ids[0], skip_special_tokens=True)
#
#            return JsonResponse({
#                'success': True,
#                'response': response
#            })
#
#        except Exception as e:
#            return JsonResponse({
#                'success': False,
#                'error': f'Ha ocurrido un error: {str(e)}'
#            })
#
#    return JsonResponse({
#        'success': False,
#        'error': 'Método no permitido'
#    })


#from django.http import JsonResponse
#from django.views.decorators.csrf import csrf_exempt
#from products.models import Product, Category
#from .models import ChatbotQuery
#import json
#import re
#from django.db import models
#from .nplutils import preprocesar_texto
#from .nplutils import corregir_texto
#from .nplutils import detectar_intencion
#from .nplutils import extraer_entidades
#from .nplutils import filtrar_stopwords
#from .nplutils import corregir_con_regex
#from .nplutils import correcciones
#
#@csrf_exempt
#def chatbot_query(request):
#    """API para procesar consultas del chatbot."""
#    if request.method == 'POST':
#        try:
#            data = json.loads(request.body)
#            query = data.get('query', '').lower()
#
#            query_corregida = corregir_texto(query)
#            query_corregida = corregir_con_regex(query_corregida, correcciones)
#            query_filtrada = filtrar_stopwords(query_corregida)
#            tokens = preprocesar_texto(query_filtrada)
#            intenciones = detectar_intencion(tokens)
#            entidades = extraer_entidades(tokens)
#
#
#            # Guardar la consulta en la base de datos
#            chat_query = ChatbotQuery(
#                query=query,  # Usamos la variable correcta
#                processed_query=query_filtrada,
#                response="",  # Inicializamos vacío
#                intent=", ".join(intenciones) if intenciones else ""  # Unimos intenciones detectadas
#            )
#
#            # Palabras clave para buscar por categoría
#            category_keywords = {
#                'portatil': 'Portátiles Gaming',
#                'laptop': 'Portátiles Gaming',
#                'notebook': 'Portátiles Gaming',
#                'gaming': None,# Buscar en todas las categorías con "gaming"
#                'juego': None,
#                'teclado': 'Periféricos',
#                'mouse': 'Periféricos',
#                'raton': 'Periféricos',
#                'auricular': 'Periféricos',
#                'cascos': 'Periféricos',
#                'tarjeta': 'Componentes',
#                'grafica': 'Componentes',
#                'procesador': 'Componentes',
#                'cpu': 'Componentes',
#                'gpu': 'Componentes',
#                'fuente de poder':"componentes",
#                'placa madre': 'Componentes',
#                'monitor': 'Monitores',
#                'pantalla': 'Monitores',
#                'silla': 'Sillas Gaming',
#            }
#
#            # Patrones para extraer información de precio
#            price_pattern = r'(?:menos de|bajo|maximo|hasta|precio|valor)\s*(\d+)\s*(?:mil|k|dólares|dolares|pesos|millon|M|)?'
#            price_match = re.search(price_pattern, query)
#            max_price = None
#
#            if price_match:
#                # Encontrar el primer grupo que no sea None
#                for group in price_match.groups():
#                    if group is not None:
#                        max_price = int(group) * 1000
#                        break
#
#            # Iniciar búsqueda de productos
#            products_query = Product.objects.filter(is_available=True)
#
#            # Respuestas especiales para saludos o preguntas generales
#            greetings = ['hola','oe','hey', 'saludos', 'buenos días','buenos dias','buenas tardes', 'buenas noches','we','wenas','wey','hey','ey','buenas','que tal','qué tal','alo','saludos','que hay','como estamos','como andamos']
#            despedida=['adios','chao','cuidate','hasta luego','hasta la proxima','adiós','nos vemos','chau','arrivederchi','gracie','nos vemos','chiao']
#            help_keywords = ['ayuda', 'ayudame', 'como funciona', 'que haces']
#
#            if any(greeting in query for greeting in greetings):
#                response = "¡Hola! Soy el asistente de TecLegacy. Puedo ayudarte a encontrar productos gaming y tecnología. ¿Qué estás buscando hoy?"
#                chat_query.response = response
#                chat_query.save()
#                return JsonResponse({
#                    'success': True,
#                    'response': response
#                })
#
#            if any(greeting in query for greeting in despedida):
#                response = "¡Adiós espero haber sido de ayuda,Vuelva Pronto"
#                chat_query.response = response
#                chat_query.save()
#                return JsonResponse({
#                    'success': True,
#                    'response': response
#                })
#
#            if any(keyword in query for keyword in help_keywords):
#                response = "Puedo ayudarte a encontrar productos en nuestra tienda. Prueba preguntándome por productos específicos como 'muéstrame teclados gaming' o 'busco un monitor de 27 pulgadas'. También puedes indicarme un rango de precio como 'monitores por menos de 500'."
#                chat_query.response = response
#                chat_query.save()
#                return JsonResponse({
#                    'success': True,
#                    'response': response
#                })
#
#            # Filtrar por categoría si se detecta una palabra clave
#            category_filter_applied = False
#            for keyword, category_name in category_keywords.items():
#                if keyword in query:
#                    if category_name:  # Si hay una categoría específica
#                        try:
#                            category = Category.objects.get(name=category_name)
#                            products_query = products_query.filter(category=category)
#                            category_filter_applied = True
#                        except Category.DoesNotExist:
#                            pass
#                    else:  # Para palabras como "gaming" que pueden estar en varias categorías
#                        products_query = products_query.filter(name__icontains=keyword)
#                        category_filter_applied = True
#
#            # Si no se aplicó filtro por categoría, buscar por nombre
#            if not category_filter_applied:
#                # Extraer palabras clave potenciales (palabras de 3+ caracteres)
#                keywords = [word for word in query.split() if len(word) >= 3]
#                for keyword in keywords:
#                    products_query = products_query.filter(
#                        models.Q(name__icontains=keyword) |
#                        models.Q(description__icontains=keyword)
#                    )
#
#            # Filtrar por precio máximo si se especificó
#            if max_price:
#                products_query = products_query.filter(price__lte=max_price)
#
#            # Limitar a 5 productos como máximo
#            products = products_query[:12]
#
#            # Crear respuesta basada en los resultados
#            if products.exists():
#                if max_price:
#                    response = f"He encontrado estos productos tacaño, por menos de ${max_price / 1000}k:<br>"
#                else:
#                    response = "He encontrado estos productos para que compre si o si:<br>"
#
#                for product in products:
#                    price_formatted = '{:,.0f}'.format(product.price).replace(',', '.')
#                    response += f"🔗 - <a href='/products/{product.category.slug}/{product.slug}/'>{product.name}</a> - ${price_formatted}<br>"
#
#                if products.count() == 12:
#                    response += "<br>Estos son solo algunos resultados. ¿Quieres más detalles o buscar algo más específico?"
#            else:
#                response = f"Lo siento, no encontré productos que coincidan con '{query}'. Prueba con otra busqueda o puedes describir mejor lo que buscas."
#
#                # Sugerir categorías disponibles
#                categories = Category.objects.filter(is_active=True)
#                if categories.exists():
#                    response += "<br><br>Puedes explorar nuestras categorías:<br>"
#                    for category in categories:
#                        response += f"🔗 - <a href='/products/{category.slug}/'>{category.name}</a><br>"
#                        response += "<br>".join([f"- {cat.name}" for cat in categories])
#
#            # Búsqueda por intenciones detectadas
#            if "precio" in intenciones and max_price:
#                products_query = products_query.filter(price__lte=max_price)
#
#            # Búsqueda por entidades (ejemplo simplificado)
#            if entidades.get("productos"):
#                for producto in entidades["productos"]:
#                     products_query = products_query.filter(
#                         models.Q(name__icontains=producto) |
#                            models.Q(description__icontains=producto)
#                    )
#
#             # Búsqueda por categorías (mejorada)
#                     # Búsqueda por categorías (mejorada)
#                     for token in tokens:
#                         if token in category_keywords:
#                             category_name = category_keywords[token]
#                             if category_name:
#                                 try:
#                                     category = Category.objects.get(name=category_name)
#                                     products_query = products_query.filter(category=category)
#                                 except Category.DoesNotExist:
#                                     pass
#
#            # Guardar la respuesta y devolver
#            chat_query.response = response
#            chat_query.save()
#
#            return JsonResponse({
#                'success': True,
#                'response': response,
#                'debug': {
#                    'original': query,
#                    'corregida': query_corregida,
#                    'filtrada': query_filtrada,
#                    'tokens': tokens,
#                    'intenciones': intenciones,
#                    'entidades': entidades
#                }
#            })
#
#        except Exception as e:
#            return JsonResponse({
#                'success': False,
#                'error': str(e)
#            })
#
#    return JsonResponse({
#        'success': False,
#        'error': 'Método no permitido'
#    })
