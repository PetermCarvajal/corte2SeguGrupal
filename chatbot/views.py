from django.views.decorators.csrf import csrf_exempt
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from .entrenar import trainer
from django.http import JsonResponse
from products.models import Category
from django.urls import reverse
import re
import json
import nltk
import spacy
from spacy.lang.es.stop_words import STOP_WORDS
from unidecode import unidecode
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from nltk.corpus import wordnet
from itertools import chain
import os
from django.urls import reverse
from products.models import Product, Category
from django.db import models


# ========== NLP SETUP ==========

try:
    nlp = spacy.load("es_core_news_sm")
except:
    import es_core_news_sm
    nlp = es_core_news_sm.load()

# ========== CHATBOT SETUP ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'chatbot_db.sqlite3')

try:
    nlp = spacy.load("es_core_news_sm")
except Exception:
    import es_core_news_sm
    nlp = es_core_news_sm.load()

# Instanciamos el chatbot (asegúrate de haber corrido previamente el entrenamiento en otro script)
chatbot = ChatBot(
    'CL4P-TP',
    logic_adapters=['chatterbot.logic.BestMatch'],
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri=f'sqlite:///{DB_PATH}'
)

# ========== VOCABULARIO ==========

SALUDOS = ['hola', 'oe', 'hey', 'saludos', 'buenos días', 'buenos dias', 'buenas tardes', 'buenas noches',
           'we', 'wenas', 'wey', 'ey', 'buenas', 'que tal', 'qué tal', 'alo', 'que hay', 'como estamos', 'como andamos']

DESPEDIDAS = ['adios', 'chao', 'cuidate', 'hasta luego', 'hasta la proxima', 'adiós', 'nos vemos', 'chau',
              'arrivederchi', 'nos vemos', 'chiao','bye']

AYUDA = ['ayuda', 'ayudame', 'como funciona', 'que haces','help']

BUSQUEDA_TRIGGERS = ["busco", "estoy buscando", "quiero ver", "necesito", "me interesa", "me gustaría ver","quiero"]

PALABRAS_ENVIO = ["envío", "envios", "envían", "hacen envíos", "despacho", "despachan","entrega", "entregas", "reparto", "reparten", "distribución",
                  "enviaremos", "mandan", "envíen", "remesa", "remesas","envio", "envian", "hacen envios", "distribucion", "envien"]

# ========== CORRECCIONES - SINÓNIMOS - DICCIONARIOS - COLECCIONES GRANDES==========

INTENCIONES = {
    "inicio": ["inicio", "volver al inicio", "home", "página principal","index"],
    "productos": ["productos", "ver productos", "mostrar productos", "catálogo","catálogo de productos","categoria","categorias","categorías","categoría",],
    "login": ["iniciar sesión", "login", "acceder", "entrar","registrarse","registro","crear cuenta"],
}

PRODUCTOS =["juegos","juegazos","jueguitos","minecraft,audifonos","diadema","auriculares","procesador","cpu","gpu","mouse","raton","escritorio",
            "teclado de membrana","teclado","teclado mecanico","teclado optico","teclados memcanicos","disipador","disiapdores","Samsung","apple",
            "huawei","xiaomi","motorola","Oppo","vivo","oneplus","realme","xbox one","xbox 360","xbox","xbox s","ps2",",ps3","ps4","ps5","play estation 2",
            "play station 3","play estation 4","play estation 5","celulares","lenovo","google","Funko","bandai","corsair","asus","hp","nintendo","ubisoft",
            "electronic arts","supercell","elgato","razer","alcatel","tcl","lego","hot toys","msi","gigabyte","thermaltake","steam deck","rockstar games",
            "activision blizard","capcom","hyperx","logitech"]

correcciones = {
    "ke": "que", "k": "que", "xq": "por que", "pa": "para", "tbn": "también", "toy": "estoy", "toi": "estoy", "dnd": "donde",
    "kiero": "quiero", "sta": "esta", "stoy": "estoy", "ntnc": "entonces", "q tal": "qué tal", "procesador amd": "procesador AMD",
    "grafica nvidia": "tarjeta gráfica NVIDIA", "grafica amd": "tarjeta gráfica AMD", "grafica": "tarjeta gráfica",
    "mouse gamer": "ratón gamer", "pantaya gamer": "pantalla gamer", "raton": "ratón", "ssd": "disco SSD",
    "hdd": "disco HDD", "celu": "celular", "lap": "laptop", "play": "PlayStation", "auris": "auriculares",
    "bn": "bien", "x": "por", "cel": "celular", "tv": "televisor", "headset": "auriculares con micrófono",
    "teclado mecaniko": "teclado mecánico","teclado mecanico": "teclado mecánico","monitor curvo": "monitor curvo",
    "pantaya": "pantalla","grafika": "tarjeta gráfica","placa madre": "placa base","board": "placa base",
    "motherboard": "placa base","memoria ram": "RAM","almacenamiento ssd": "disco SSD","almacenamiento hdd": "disco HDD",
    "gabinete gamer": "torre gamer","case": "torre","fuente poder": "fuente de poder","fuente": "fuente de poder",
    "ventilador rgb": "ventilador RGB","cooler": "disipador","silla gammer": "silla gamer","silla gamer": "silla gamer",
    "escritorio gamer": "mesa gamer","control play": "control de PlayStation","control xbox": "control de Xbox",
    "xbox x": "Xbox Series X","xbox s": "Xbox Series S","ps5": "PlayStation 5","ps4": "PlayStation 4",
    "nintendo switch": "Nintendo Switch","switch oled": "Nintendo Switch OLED","switch lite": "Nintendo Switch Lite",
    "minecra": "Minecraft","mincraf": "Minecraft","micraf": "Minecraft","fortnait": "Fortnite","fornite": "Fortnite",
    "jueguitos": "videojuegos","jueguito": "videojuego","usb": "memoria USB","micro sd": "tarjeta MicroSD",
    "cargador cel": "cargador de celular","cargador lap": "cargador de laptop","pc gamer": "PC Gamer","notebook": "laptop",
    "cpu": "procesador","gpu": "tarjeta gráfica","cámara": "cámara web","camara": "cámara","porq": "porque","xk": "porque",
    "pq": "porque","asi que": "así que","nose": "no sé","aunqueh": "aunque","en tonces": "entonces","tonces": "entonces",
    "entonses": "entonces","dsp": "después","luegp": "luego","depues": "después","ademas": "además",
    "aparte de eso": "además","por lo tanto": "por lo tanto","asi ": "asimismo","por otro lado": "por otro lado",
    "en cambio": "en cambio","tal vez": "tal vez","de hecho": "de hecho","aci que": "así que","noc": "no sé","noce": "no sé",
    "aun que": "aunque","anque": "aunque","desp": "después","despue": "después","de mas": "además","admas": "además",
    "sinembargo": "sin embargo","sin enbargo": "sin embargo","sin en vargo": "sin embargo","porlo tanto": "por lo tanto",
    "por lo tnto": "por lo tanto","por lotanto": "por lo tanto","asi mismo": "asimismo","así mismo": "asimismo",
    "asi mismoo": "asimismo","por consiguiente": "por consiguiente","por consiquiente": "por consiguiente",
    "por consigiente": "por consiguiente","en conclusion": "en conclusión","conclucion": "conclusión",
    "en conclución": "en conclusión","en resumen": "en resumen","resumiendo": "en resumen","por ejemplo": "por ejemplo",
    "xej": "por ejemplo","ejem": "por ejemplo","en fin": "en fin","enfin": "en fin","al final": "al final",
    "alfinal": "al final","es decir": "es decir","osea": "o sea","ose": "o sea","o sea": "o sea","talvez": "tal vez",
    "tal ves": "tal vez","talves": "tal vez","quizas": "quizás","quiza": "quizá","kizas": "quizás","kisa": "quizá",
    "deecho": "de hecho","de echo": "de hecho","valla": "vaya","vaya": "vaya","vaya a": "vaya a","tenga": "tenga",
    "que tenga": "que tenga","un": "un","una": "una","unos": "unos","unas": "unas","con": "con","i": "y","u":"u",
    "por ke": "porque","ya qe": "ya que","ya ke": "ya que","yaque": "ya que","pues": "pues","puez": "pues",
    "puesto qe": "puesto que","puesto ke": "puesto que","puesto que": "puesto que","dado qe": "dado que",
    "dado ke": "dado que","dado que": "dado que","debido a que": "debido a que","debuidoi a q": "debido a que",
    "x eso": "por eso","por eso": "por eso","por eso mismo": "por eso mismo","mejor dicho": "mejor dicho",
    "en otras palabras": "en otras palabras","vale decir": "vale decir","esto es": "esto es","estoes": "esto es",
    "mejor dixo": "mejor dicho","es dcir": "es decir","en primer lugar": "en primer lugar","primeramente": "primeramente",
    "segundo": "segundo","en segundo lugar": "en segundo lugar","por último": "por último","finalmente": "finalmente",
    "para terminar": "para terminar","para concluir": "para concluir","en conclucion": "en conclusión",
    "enconclusion": "en conclusión","hbaer":"a ver","haber":"a ver","alla":"haya","aserca": "acerca","aser": "hacer",
    "aserlo": "hacerlo","aver": "a ver","abeses": "a veces","avesez": "a veces","ahy": "hay","ahi": "ahí","hay": "hay",
    "ay": "hay","ahy que": "hay que","ay que": "hay que","oi": "hoy","oi dia": "hoy día","oir": "oír","toa": "toda",
    "to": "todo","na": "nada","q onda": "qué onda","holi": "hola","aki": "aquí","aki toy": "aquí estoy","toy bn": "estoy bien",
    "bno": "bueno","klk": "¿qué tal?","intel i5": "Intel i5","intel i7": "Intel i7","disco duro externo": "HDD externo",
    "memoria externa": "almacenamiento externo","microfon": "micrófono","micro": "micrófono","cascos": "audífonos",
    "auris gamer": "auriculares gamer","lsta":"lista","articulso":"articulos","lapto":"laptop","laotop":"laptop",
    "compu":"computador",
}

sinonimos_productos = {
    "celular": ["teléfono", "móvil", "smartphone"],
    "tv": ["televisor", "pantalla", "television"],
    "pc": ["computadora", "ordenador", "pc gamer", "computador"],
    "laptop": ["notebook", "portátil", "laptop"],
    "monitor": ["pantalla", "display", "monitor gamer"],
    "ratón": ["mouse", "ratón gamer", "mouse gamer"],
    "teclado": ["teclado gamer", "teclado mecánico"],
    "auriculares": ["audífonos", "auris", "headset"],
    "juegos": ["video juegos", "jueguitos", "juegazos"]
}

PAISES = [
    "afganistan", "albania", "alemania", "andorra", "angola", "antigua y barbuda", "arabia saudita",
    "argelia", "argentina", "armenia", "australia", "austria", "azerbaiyan", "bahamas", "banglades",
    "barbados", "barein", "belgica", "belice", "benin", "bielorrusia", "birmania", "bolivia",
    "bosnia y herzegovina", "botsuana", "brasil", "brunei", "bulgaria", "burkina faso", "burundi",
    "butan", "cabo verde", "camboya", "camerun", "canada", "catar", "chad", "chile", "china",
    "chipre", "colombia", "comoras", "corea del norte", "corea del sur", "costa de marfil",
    "costa rica", "croacia", "cuba", "dinamarca", "dominica", "ecuador", "egipto", "el salvador",
    "emiratos arabes unidos", "eritrea", "eslovaquia", "eslovenia", "espana", "estados unidos",
    "estonia", "esuatini", "etiopia", "filipinas", "finlandia", "francia", "gabon", "gambia",
    "georgia", "ghana", "granada", "grecia", "guatemala", "guinea", "guinea-bisau",
    "guinea ecuatorial", "guyana", "haiti", "honduras", "hungria", "india", "indonesia", "irak",
    "iran", "irlanda", "islandia", "islas marshall", "islas salomon", "israel", "italia", "jamaica",
    "japon", "jordania", "kazajistan", "kenia", "kirguistan", "kiribati", "kuwait", "laos",
    "lesoto", "letonia", "libano", "liberia", "libia", "liechtenstein", "lituania", "luxemburgo",
    "madagascar", "malasia", "malaui", "maldivas", "mali", "malta", "marruecos", "mauricio",
    "mauritania", "mexico", "micronesia", "moldavia", "monaco", "mongolia", "montenegro",
    "mozambique", "namibia", "nauru", "nepal", "nicaragua", "niger", "nigeria", "noruega",
    "nueva zelanda", "oman", "paises bajos", "pakistan", "palaos", "palestina", "panama",
    "papua nueva guinea", "paraguay", "peru", "polonia", "portugal", "reino unido",
    "republica centroafricana", "republica checa", "republica del congo",
    "republica democratica del congo", "republica dominicana", "ruanda", "rumania", "rusia",
    "san cristobal y nieves", "san marino", "san vicente y las granadinas", "santa lucia",
    "santo tome y principe", "senegal", "serbia", "seychelles", "sierra leona", "singapur",
    "siria", "somalia", "sri lanka", "sudafrica", "sudan", "sudan del sur", "suecia", "suiza",
    "surinam", "tailandia", "tanzania", "tayikistan", "timor oriental", "togo", "tonga",
    "trinidad y tobago", "tunez", "turkmenistan", "turquia", "tuvalu", "ucrania", "uganda",
    "uruguay", "uzbekistan", "vanuatu", "vaticano", "venezuela", "vietnam", "yemen", "yibuti",
    "zambia", "zimbabue"
]

category_keywords = {
                'portatil': 'Portátiles Gaming',
                'laptop': 'Portátiles Gaming',
                'notebook': 'Portátiles Gaming',
                'gaming': None,
                'juego': None,
                'teclado': 'Periféricos',
                'mouse': 'Periféricos',
                'raton': 'Periféricos',
                'auricular': 'Periféricos',
                'cascos': 'Periféricos',
                'tarjeta': 'Componentes',
                'grafica': 'Componentes',
                'procesador': 'Componentes',
                'cpu': 'Componentes',
                'placa': 'Componentes',
                'monitor': 'Monitores',
                'pantalla': 'Monitores',
                'silla': 'Sillas Gaming',
            }

# ========== NLP FUNCTIONS ==========

def generar_sinonimos(frase):
    palabras = frase.lower().split()
    frases_sinonimos = []
    for i, palabra in enumerate(palabras):
        sinonimos = wordnet.synsets(palabra)
        sinonimos = set(chain.from_iterable([s.lemma_names() for s in sinonimos]))
        for sinonimo in sinonimos:
            nueva = palabras.copy()
            nueva[i] = sinonimo.replace('_', ' ')
            frases_sinonimos.append(" ".join(nueva))
    return list(set(frases_sinonimos))

def guardar_pregunta_desconocida(pregunta):
    with open("preguntas_nuevas.txt","a",encoding="utf-8") as f:
        f.write(pregunta+"\n")

def corregir_con_regex(texto, correcciones):
    patron = re.compile(r'\b(' + '|'.join(re.escape(k) for k in correcciones.keys()) + r')\b')
    return patron.sub(lambda x: correcciones[x.group()], texto.lower())

def preprocesar_texto(texto):
    texto = unidecode(texto.lower())
    texto = re.sub(r'[^\w\s]', '', texto)
    doc = nlp(texto)
    return [token.lemma_ for token in doc if not token.is_stop and len(token.text) > 2]

def es_pregunta_envio(mensaje):
    mensaje = mensaje.lower()
    return any(palabra in mensaje for palabra in PALABRAS_ENVIO)

def detectar_intencion(texto):
    texto_corregido = corregir_con_regex(texto, correcciones)
    texto_preprocesado = ' '.join(preprocesar_texto(texto_corregido))
    if re.search(r'\b(hola|buenas|ola|klk|holi)\b', texto_preprocesado):
        return "saludo"
    if re.search(r'\b(adios|chao|nos vemos|bye)\b', texto_preprocesado):
        return "despedida"
    if re.search(r'\b(tienen|quiero|busco|venden|hay|tienen envio)\b', texto_preprocesado):
        return "pregunta_producto"
    if re.search(r'\b(precio|cuesta|vale|cuánto)\b', texto_preprocesado):
        return "pregunta_precio"
    if re.search(r'\b(envio|envían|mandan|llegan)\b', texto_preprocesado):
        return "pregunta_envio"
    if re.search(r'\b(jajaja|xd|wtf|lol)\b', texto_preprocesado):
        return "chiste"
    return "intencion_desconocida"

def detectar_producto(texto):
    texto_corregido = corregir_con_regex(texto, correcciones)
    for producto, sinonimos in sinonimos_productos.items():
        for s in sinonimos:
            if re.search(r'\b' + re.escape(s) + r'\b', texto_corregido):
                return producto
    return None

def detectar_pais_en_mensaje(mensaje):
    mensaje = mensaje.lower()
    for pais in PAISES:
        if pais in mensaje:
            return pais
    return None

def detectar_busqueda(texto_usuario):
    texto = texto_usuario.lower()
    for trigger in BUSQUEDA_TRIGGERS:
        if trigger in texto:
            partes = texto.split(trigger, 1)
            if len(partes) > 1:
                producto = partes[1].strip()
                if producto:
                    return f"¡Entendido! Puedes buscar '{producto}' desde la barra de búsqueda 🔍 en la parte superior de la página."

    # Fallback con PRODUCTOS
    for prod in PRODUCTOS:
        if prod in texto:
            return f"¡Claro! Puedes buscar '{prod}' desde la barra de búsqueda 🔍 en la parte superior de la página."

    return None

def responder_usuario(texto):
    intencion = detectar_intencion(texto)
    producto = detectar_producto(texto)
    texto_corregido = corregir_con_regex(texto, correcciones)

    if intencion == "saludo":
        return "¡Hola! 👋 ¿En qué puedo ayudarte hoy?"
    elif intencion == "despedida":
        return "¡Hasta luego! Gracias por visitar TecLegacy 💻"
    elif intencion == "pregunta_producto":
        if producto:
            return f"¡Claro! Tenemos varias opciones de {producto}. ¿Buscas algo en específico?"
        else:
            return "¿Qué producto estás buscando exactamente? Tengo muchas opciones para mostrarte."
    elif intencion == "pregunta_precio":
        if producto:
            return f"El precio de {producto} depende del modelo. ¿Quieres que te muestre opciones?"
        else:
            return "¿De qué producto quieres saber el precio?"
    elif intencion == "pregunta_envio":
        pais_detectado = detectar_pais_en_mensaje(texto)
        if pais_detectado and pais_detectado != "colombia":
            return f"Actualmente no realizamos envíos a {pais_detectado.title()}. Solo hacemos envíos nacionales dentro de Colombia."
        elif pais_detectado == "colombia":
            return "¡Claro que Sí, hacemos envíos a Toda Colombia. ✈️📦🚗"
        else:
            return chatbot.get_response(response)
    elif intencion == "chiste":
        return "Jajaja 😂 ¡Tú sí que sabes bromear! Pero también sé de hardware si necesitas ayuda 😎"
    else:
        respuesta = chatbot.get_response(texto_corregido)
        if float(respuesta.confidence) < 0.70:
            guardar_pregunta_desconocida(texto)
            print("CL4P-TP:No estoy seguro de cómo responder eso aún. ¡Lo guardaré para aprender!🧠")
            return "Lo siento, no entendí muy bien tu mensaje. ¿Podrías reformularlo o ser un poco más específico?"
        else:
            return str(respuesta)
# ========== DJANGO VIEW ==========

@csrf_exempt
def chatbot_query(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '').strip().lower()
            query_corregida = corregir_con_regex(query, correcciones)

            if not query_corregida:
                return JsonResponse({'success': False, 'error': 'Consulta vacía.'})

            # Primero intentamos con respuesta personalizada
            respuesta_personalizada = responder_usuario(query_corregida)
            if respuesta_personalizada:
                return JsonResponse({'success': True, 'response': respuesta_personalizada})

            # Si no hay intención clara, usamos el modelo ChatterBot
            response = chatbot.get_response(query_corregida)
            return JsonResponse({'success': True, 'response': str(response)})

        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Ha ocurrido un error: {str(e)}'})

    return JsonResponse({'success': False, 'error': 'Método no permitido'})

# ========== RESPUESTAS DINAMICAS - RESPUESTAS ESTATICAS ==========
def obtener_productos_desde_query(query):
    query = query.lower()

    category_keywords = {
        'portatil': 'Portátiles Gaming',
        'laptop': 'Portátiles Gaming',
        'notebook': 'Portátiles Gaming',
        'gaming': None,
        'juego': None,
        'teclado': 'Periféricos',
        'mouse': 'Periféricos',
        'raton': 'Periféricos',
        'auricular': 'Periféricos',
        'cascos': 'Periféricos',
        'tarjeta': 'Componentes',
        'grafica': 'Componentes',
        'procesador': 'Componentes',
        'cpu': 'Componentes',
        'placa': 'Componentes',
        'monitor': 'Monitores',
        'pantalla': 'Monitores',
        'silla': 'Sillas Gaming',
    }

    price_pattern = r'menos de (\d+)|bajo (\d+)|maximo (\d+)|hasta (\d+)'
    price_match = re.search(price_pattern, query)
    max_price = None

    if price_match:
        for group in price_match.groups():
            if group is not None:
                max_price = int(group) * 1000
                break

    products_query = Product.objects.filter(is_available=True)
    category_filter_applied = False

    for keyword, category_name in category_keywords.items():
        if keyword in query:
            if category_name:
                try:
                    category = Category.objects.get(name=category_name)
                    products_query = products_query.filter(category=category)
                    category_filter_applied = True
                except Category.DoesNotExist:
                    pass
            else:
                products_query = products_query.filter(name__icontains=keyword)
                category_filter_applied = True

    if not category_filter_applied:
        keywords = [word for word in query.split() if len(word) >= 3]
        for keyword in keywords:
            products_query = products_query.filter(
                models.Q(name__icontains=keyword) |
                models.Q(description__icontains=keyword)
            )

    if max_price:
        products_query = products_query.filter(price__lte=max_price)

    return products_query[:5], max_price

def chatbot_response(request):
    if request.method == "POST":
        user_input = request.POST.get("message", "").lower()

        # Respuestas estáticas
        if "inicio" in user_input:
            return JsonResponse({"response": reverse("products:index")})
        if "ver productos" in user_input or "todos los productos" in user_input:
            return JsonResponse({"response": reverse("products:product_list")})

        # PRIMERO: intenta detectar productos desde el query personalizado
        productos, max_price = obtener_productos_desde_query(user_input)
        if productos.exists():
            respuesta = generar_respuesta_con_links(productos, max_price)
            return JsonResponse({"response": respuesta})

        # SI NO: intenta detectar si se refiere a una categoría exacta
        for category in Category.objects.all():
            if category.name.lower() in user_input:
                return JsonResponse({
                    "response": reverse("products:products_by_category", args=[category.slug])
                })

        # POR ÚLTIMO: Fallback a búsqueda general
        return JsonResponse({
            "response": f"{reverse('products:search')}?q={user_input}"
        })

def detectar_busqueda(texto_usuario):
    patron = r"(busco|estoy buscando|quiero ver|necesito) (una|un|unos|unas)? (.+)"
    match = re.search(patron, texto_usuario, re.IGNORECASE)
    if match:
        producto = match.group(3)
        return f"¡Entendido! Puedes buscar '{producto}' desde la barra de búsqueda 🔍 en la parte superior de la página."
    return None

def generar_respuesta_con_links(products, max_price=None):
    if not products.exists():
        return "Lo siento, no encontré productos que coincidan con tu búsqueda."

    if max_price:
        response = f"He encontrado estos productos por menos de ${max_price / 1000}k:<br>"
    else:
        response = "He encontrado estos productos para ti:<br>"

    for product in products:
        price_formatted = '{:,.0f}'.format(product.price).replace(',', '.')
        response += f"- <a href='/products/{product.category.slug}/{product.slug}/'>{product.name}</a> - ${price_formatted}<br>"

    if products.count() == 5:
        response += "<br>Estos son solo algunos resultados. ¿Quieres más detalles o buscar algo más específico?"

    return response

MARCAS = ['asus', 'lenovo', 'apple', 'hp', 'msi', 'gigabyte', 'razer', 'hyperx', ...]
def detectar_marca(texto):
    texto = unidecode(texto.lower())
    for marca in MARCAS:
        if marca in texto:
            return marca
    return None

def detectar_productos(texto):
    texto_corregido = corregir_con_regex(texto, correcciones)
    encontrados = set()
    for producto, sinonimos in sinonimos_productos.items():
        for s in sinonimos:
            if re.search(r'\b' + re.escape(s) + r'\b', texto_corregido):
                encontrados.add(producto)
    return list(encontrados)
