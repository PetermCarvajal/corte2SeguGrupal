from spacy.lang.es.stop_words import STOP_WORDS as spacy_stop_words
from django.http import JsonResponse, HttpResponseRedirect # Necesario para redirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect # Más directo para redirecciones
from django.http import JsonResponse
from urllib.parse import quote_plus
from products.models import Product
from django.shortcuts import render
from nltk.corpus import wordnet
from django.urls import reverse
from unidecode import unidecode
from django.db.models import Q
from chatterbot import ChatBot
from django.db import models
from itertools import chain
import traceback
import datetime # Para logging con timestamp
import random # Para variar respuestas
import spacy
import nltk
import json
import re
import os

try:
    from products.models import Product, Category
except ImportError:
    print("Error: No se pudieron importar los modelos...")
    class DummyModel:
        objects = None
        DoesNotExist = Exception
        MultipleObjectsReturned = Exception
        def filter(self, *args, **kwargs): return self
        def get(self, *args, **kwargs): raise self.DoesNotExist
        def all(self): return []
        def exists(self): return False
        def first(self): return None
        def count(self): return 0
        def distinct(self): return self
        def order_by(self, *args): return self
        def __iter__(self): yield from []
        def __getitem__(self, key): return []
    Product = Category = DummyModel()

# ========== Cargar Modelo Spacy ==========

NLP_MODEL_NAME = "es_core_news_sm"
try:#2
    nlp = spacy.load(NLP_MODEL_NAME)
except OSError:
    print(f"Modelo Spacy '{NLP_MODEL_NAME}' no encontrado. Descargando...")#Nicolas y Johan cuando terminen quiten todo esto
    try:
        spacy.cli.download(NLP_MODEL_NAME)
        import importlib
        module = importlib.import_module(NLP_MODEL_NAME)
        nlp = module.load()
    except Exception as e:
        print(f"Error al descargar o cargar el modelo Spacy '{NLP_MODEL_NAME}': {e}")
        print("El chatbot podría no funcionar correctamente sin el modelo NLP.")
        nlp = None # Marcar que nlp no está disponible

# ========== CHATBOT SETUP ==========

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,'chatbot_db.sqlite3')
chatbot = ChatBot(
    'CL4P-TP',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri=f'sqlite:///{DB_PATH}',
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'Lo siento, no estoy seguro de cómo responder a eso. ¿Podrías preguntarme de otra forma?',
            'maximum_similarity_threshold': 0.90
        }
    ]
    # read_only=True # Poner en True en producción
)
LOG_FILE_PATH = os.path.join(BASE_DIR, 'registro_ingreso_texto.txt')

# ========== VOCABULARIO Y CONFIGURACIONES ==========

SALUDOS = ['hola', 'oe', 'hey', 'saludos', 'buenos días', 'buenos dias', 'buenas tardes', 'buenas noches',#3
           'we', 'wenas', 'wey', 'ey', 'buenas', 'que tal', 'qué tal', 'alo', 'que hay', 'como estamos', 'como andamos', 'oli', 'holis','holiwis']

DESPEDIDAS = ['adios', 'chao', 'cuidate', 'hasta luego', 'hasta la proxima', 'adiós', 'nos vemos', 'chau',#4
              'arrivederchi', 'nos vemos', 'chiao','bye', 'hasta pronto']

AYUDA = ['ayuda', 'ayudame', 'como funciona', 'que haces','help', 'info', 'informacion','help']#5

BUSQUEDA_TRIGGERS = ["busco", "estoy buscando", "quiero ver", "necesito", "me interesa", "me gustaría ver","quiero", "buscando"]#6

PALABRAS_ENVIO = ["envío", "envios", "envían", "hacen envíos", "despacho", "despachan","entrega", "entregas", "reparto", "reparten", "distribución", #7
                   "enviaremos", "mandan", "envíen", "remesa", "remesas","envio", "envian", "hacen envios", "distribucion", "envien", "llegan", "llega"]

INTENCIONES = {#8
    "inicio": ["inicio", "volver al inicio", "home", "página principal","index", "principal"],
    "productos": ["productos", "ver productos", "mostrar productos", "catálogo","catálogo de productos","categoria","categorias","categorías","categoría", "tienda", "ver tienda", "catalogo"],
    "login": ["iniciar sesión", "login", "acceder", "entrar","registrarse","registro","crear cuenta", "mi cuenta"],
}

PRODUCTOS =["juegos","juegazos","jueguitos","minecraft","audifonos","diadema","auriculares","procesador","cpu","gpu","mouse","raton","escritorio",#9
            "teclado de membrana","teclado","teclado mecanico","teclado optico","teclados memcanicos","disipador","disiapdores","Samsung","apple",
            "huawei","xiaomi","motorola","Oppo","vivo","oneplus","realme","xbox one","xbox 360","xbox","xbox s","ps2","ps3","ps4","ps5","play estation 2",
            "play station 3","play estation 4","play estation 5","celulares","lenovo","google","Funko","bandai","corsair","asus","hp","nintendo","ubisoft",
            "electronic arts","supercell","elgato","razer","alcatel","tcl","lego","hot toys","msi","gigabyte","thermaltake","steam deck","rockstar games",
            "activision blizard","capcom","hyperx","logitech", "tarjeta grafica", "ram", "memoria ram", "placa base", "fuente poder", "monitor", "pantalla",
            "silla gamer", "refrigeracion liquida", "ventilador", "portatil", "laptop", "notebook"]

correcciones = {#10
    "ke": "que", "k": "que", "xq": "por que", "pa": "para", "tbn": "también", "toy": "estoy", "toi": "estoy", "dnd": "donde",
    "kiero": "quiero", "sta": "esta", "stoy": "estoy", "ntnc": "entonces", "q tal": "qué tal", "procesador amd": "procesador AMD",
    "grafica nvidia": "tarjeta gráfica NVIDIA", "grafica amd": "tarjeta gráfica AMD", "grafica": "tarjeta gráfica", "gpu": "tarjeta gráfica",
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
    "miencraft": "minecraft", "minecra": "minecraft", "mincraf": "minecraft", "micraf": "minecraft",
    "fortnait": "Fortnite","fornite": "Fortnite", "fortnai": "Fortnite",
    "jueguitos": "videojuegos","jueguito": "videojuego","usb": "memoria USB","micro sd": "tarjeta MicroSD",
    "cargador cel": "cargador de celular","cargador lap": "cargador de laptop","pc gamer": "PC Gamer","notebook": "laptop",
    "cpu": "procesador","cámara": "cámara web","camara": "cámara","porq": "porque","xk": "porque",
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
    "que tenga": "que tenga","i": "y","u":"u", "refrigeracion": "refrigeración", "liquida": "líquida",
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
    "compu":"computador","telcado":"teclado","raotn":"ratón"
}

# Diccionario de sinónimos para normalizar términos de productos
sinonimos_productos = {#11
    "celular": ["teléfono", "móvil", "smartphone", "cel"],
    "tv": ["televisor", "pantalla", "television"],
    "pc": ["computadora", "ordenador", "pc gamer", "computador", "compu", "cpu"],
    "laptop": ["notebook", "portátil", "lap"],
    "monitor": ["pantalla", "display", "monitor gamer"],
    "ratón": ["mouse", "ratón gamer", "mouse gamer"],
    "teclado": ["teclado gamer", "teclado mecánico", "teclado optico", "teclado membrana"],
    "auriculares": ["audífonos", "auris", "headset", "cascos", "diadema"],
    "juegos": ["video juegos", "jueguitos", "juegazos", "videojuegos", "juego"],
    "tarjeta gráfica": ["grafica", "gpu", "tarjeta de video"],
    "procesador": ["cpu", "microprocesador"],
    "ram": ["memoria", "memoria ram"],
    "disco": ["almacenamiento", "disco duro", "ssd", "hdd"],
    "silla": ["silla gamer", "silla de escritorio"]
}

# Lista de países (para preguntas de envío) - Asegúrate que esté en minúsculas y sin tildes
PAISES = [#12
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
    "samoa", "san cristobal y nieves", "san marino", "san vicente y las granadinas", "santa lucia",
    "santo tome y principe", "senegal", "serbia", "seychelles", "sierra leona", "singapur",
    "siria", "somalia", "sri lanka", "sudafrica", "sudan", "sudan del sur", "suecia", "suiza",
    "surinam", "tailandia", "tanzania", "tayikistan", "timor oriental", "togo", "tonga",
    "trinidad y tobago", "tunez", "turkmenistan", "turquia", "tuvalu", "ucrania", "uganda",
    "uruguay", "uzbekistan", "vanuatu", "vaticano", "venezuela", "vietnam", "yemen", "yibuti",
    "zambia", "zimbabue"
]

category_keywords = {
   # Portátiles Gaming
   'portatil': 'Portátiles Gaming', 'portátil': 'Portátiles Gaming', 'laptop': 'Portátiles Gaming',
   'notebook': 'Portátiles Gaming', 'ultrabook': 'Portátiles Gaming',
   # Consolas y Videojuegos
   'gaming': 'Consolas y Videojuegos', 'juego': 'Consolas y Videojuegos',
   'consola': 'Consolas y Videojuegos', 'videojuego': 'Consolas y Videojuegos',
   'xbox': 'Consolas y Videojuegos', 'playstation': 'Consolas y Videojuegos',
   'ps4': 'Consolas y Videojuegos', 'ps5': 'Consolas y Videojuegos',
   'nintendo': 'Consolas y Videojuegos',
   # Periféricos
   'teclado': 'Periféricos', 'keyboard': 'Periféricos',
   'mouse': 'Periféricos', 'raton': 'Periféricos',
   'auricular': 'Periféricos', 'audifono': 'Periféricos',
   'headset': 'Periféricos', 'cascos': 'Periféricos',
   'diadema': 'Periféricos', 'periferico': 'Periféricos',
   'periférico': 'Periféricos', 'microfono': 'Periféricos',
   'micrófono': 'Periféricos',
   # Componentes
   'tarjeta': 'Componentes', 'grafica': 'Componentes',
   'tarjeta grafica': 'Componentes', 'gpu': 'Componentes',
   'video': 'Componentes', 'procesador': 'Componentes',
   'cpu': 'Componentes', 'ram': 'Componentes',
   'memoria': 'Componentes', 'placa': 'Componentes',
   'board': 'Componentes', 'motherboard': 'Componentes',
   'disco': 'Componentes', 'ssd': 'Componentes',
   'hdd': 'Componentes', 'almacenamiento': 'Componentes',
   'fuente': 'Componentes', 'poder': 'Componentes',
   'componente': 'Componentes',
   # Monitores
   'monitor': 'Monitores', 'pantalla': 'Monitores',
   'display': 'Monitores',
   # Sillas Gaming
   'silla': 'Sillas Gaming', 'silla gamer': 'Sillas Gaming',
   'silla gaming': 'Sillas Gaming',
   # Muebles y Accesorios
   'escritorio': 'Muebles y Accesorios', 'mueble': 'Muebles y Accesorios',
   'accesorio': 'Muebles y Accesorios', 'mesa': 'Muebles y Accesorios',
   'soporte': 'Muebles y Accesorios', 'organizador': 'Muebles y Accesorios',
   # Refrigeración
   'refrigeracion': 'Refrigeración', 'refrigeración': 'Refrigeración',
   'ventilador': 'Refrigeración', 'cooler': 'Refrigeración',
   'disipador': 'Refrigeración', 'liquida': 'Refrigeración',
   'watercooling': 'Refrigeración', 'radiador': 'Refrigeración'
}

PALABRAS_A_IGNORAR = set(spacy_stop_words) | set(BUSQUEDA_TRIGGERS) | {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "a", "en",
    "y", "o", "pero", "si", "no", "es", "son", "este", "esta", "estos", "estas",
    "ser", "estar", "tener", "hacer", "ir", "poder", "deber", "querer", "mi", "tu",
    "su", "nuestro", "vuestro", "me", "te", "se", "nos", "os", "le", "les", "al",
    "lo", "con", "para", "por", "más", "muy", "poco", "mucho", "bien", "mal", "así",
    "como", "cuando", "donde", "quien", "cuales", "cual", "algo", "nada", "todo",
    "todos", "todas", "uno", "dos", "tres", "u", "e", "ni", "sin", "sobre", "tras",
    "ante", "bajo", "cabe", "contra", "desde", "durante", "hacia", "hasta", "mediante",
    "según", "so", "también", "tampoco", "quizás", "tal vez", "vez", "ya", "aun",
    "aunque", "porque", "pues", "siempre", "nunca", "jamás", "ahora", "hoy", "ayer",
    "mañana", "aquí", "allí", "allá", "esto", "eso", "aquello", "hay", "era", "fue",
    "sería", "había", "habrá", "he", "has", "ha", "hemos", "habéis", "han", "estoy",
    "estás", "está", "estamos", "estáis", "están", "fui", "fuiste", "fuimos",
    "fuisteis", "fueron", "iré", "irás", "irá", "iremos", "iréis", "irán", "tenido",
    "tenías", "tenía", "teníamos", "teníais", "tenían", "hice", "hiciste", "hizo",
    "hicimos", "hicisteis", "hicieron", "pude", "pudiste", "pudo", "pudimos", "pudisteis",
    "pudieron", "debí", "debiste", "debió", "debimos", "debisteis", "debieron", "quise",
    "quisiste", "quiso", "quisimos", "quisisteis", "quisieron", ",", ".", ";", ":",
    "¿", "?", "¡", "!", "(", ")", "[", "]", "{", "}", "'", '"', "-", "_", "+", "=",
    "*", "/", "<", ">", "~", "^", "`", "|", "\\", "@", "#", "$", "%", "&",
    'comprar', 'ver', 'mostrar', 'dame', 'precio', 'costo', 'valor', 'cotizar',
    'cuanto', 'cuesta', 'vale', 'tienen', 'tienes', 'venden', 'ofrecen',
    'favor', 'porfa', 'porfis', 'quisiera', 'info', 'informacion', 'ayuda'
}

MARCAS = ['asus', 'lenovo', 'apple', 'hp', 'msi', 'gigabyte', 'razer', 'hyperx', 'logitech',#15
          'corsair', 'samsung', 'lg', 'acer', 'dell', 'intel', 'amd', 'nvidia', 'kingston',
          'seagate', 'western digital', 'wd', 'adata', 'crucial', 'evga', 'thermaltake',
          'cooler master', 'nzxt', 'lian li', 'be quiet', 'steelseries', 'microsoft', 'sony',
          'nintendo', 'xbox', 'playstation','poco','nubia','asus rog','aorus','gigabyte','tukasa','msi','nzxt','nvidia','microsoft','mojang']

# ========== FUNCIONES HELPER NLP ==========

def log_user_input(query, source):
    """Registra la consulta cruda del usuario, timestamp y origen."""
    if not query:
        return  # No registrar consultas vacías
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Usar repr(query) para manejar caracteres especiales y saltos de línea
        log_entry = f"{timestamp} [{source.upper()}] - {repr(query)}\n"
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error al escribir en log '{LOG_FILE_PATH}': {e}")

def generar_sinonimos(frase):#16
    """Genera frases alternativas usando sinónimos de WordNet."""
    palabras = frase.lower().split()
    frases_sinonimos = [frase]
    try:
        for i, palabra in enumerate(palabras):
            sinonimos_Lemmas = set()
            for syn in wordnet.synsets(palabra, lang='spa'):
                 for lemma in syn.lemmas(lang='spa'):
                     sinonimos_Lemmas.add(lemma.name().replace('_', ' '))

            for sinonimo in sinonimos_Lemmas:
                if palabra != sinonimo:
                    nueva = palabras.copy()
                    nueva[i] = sinonimo
                    frases_sinonimos.append(" ".join(nueva))
    except Exception as e:
        print(f"Error al generar sinónimos para '{frase}': {e}")
    return list(set(frases_sinonimos)) # Devolver lista única

def guardar_pregunta_desconocida(pregunta): #17 (Guardar pregunta no entendida)
    """Guarda la pregunta no respondida en un archivo para revisión."""
    log_user_input(f"Pregunta Desconocida: {pregunta}", "SYSTEM")  # 👈 EXTRA
    try:
        with open("preguntas_nuevas.txt", "a", encoding="utf-8") as f:
            f.write(pregunta + "\n")
    except Exception as e:
        print(f"Error al guardar pregunta desconocida: {e}")

def corregir_con_regex(texto, dict_correcciones): #18
    """Aplica correcciones básicas usando un diccionario y regex."""
    if not texto or not isinstance(texto, str):
        return ""
    patron = re.compile(r'\b(' + '|'.join(re.escape(k) for k in dict_correcciones.keys()) + r')\b', re.IGNORECASE)
    texto_lower = texto.lower()
    texto_corregido = patron.sub(lambda x: dict_correcciones.get(x.group().lower(), x.group()), texto_lower)
    return texto_corregido

def preprocesar_texto(texto):#19
    """Lematiza y elimina stop words (versión simplificada)."""
    if not nlp or not texto or not isinstance(texto, str):
        return []
    texto_normalizado = unidecode(texto.lower())
    texto_limpio = re.sub(r'[^\w\s]', '', texto_normalizado)
    doc = nlp(texto_limpio)
    return [token.lemma_ for token in doc if not token.is_stop and len(token.text) > 2]

def extraer_palabras_clave(texto_usuario):#20
    """
    Limpia la consulta del usuario para extraer solo las palabras clave
    relevantes para la búsqueda de productos o categorías.
    """
    if not nlp or not texto_usuario or not isinstance(texto_usuario, str):
        return ""

    texto_limpio = texto_usuario.lower()
    doc = nlp(texto_limpio)

    palabras_clave = []
    for token in doc:
        lema = token.lemma_
        if not token.is_punct and not token.is_space and \
           lema not in PALABRAS_A_IGNORAR and \
           token.text not in PALABRAS_A_IGNORAR:
            palabras_clave.append(token.text)
    resultado = " ".join(palabras_clave).strip()
    resultado = " ".join(list(dict.fromkeys(resultado.split())))
    return resultado

def es_pregunta_envio(mensaje):#21
    """Verifica si el mensaje contiene palabras clave de envío."""
    mensaje_lower = unidecode(mensaje.lower())
    return any(palabra in mensaje_lower for palabra in PALABRAS_ENVIO)

def detectar_intencion(texto):#22
    """Detecta intenciones básicas (saludo, despedida, envío, etc.)."""
    if not texto or not isinstance(texto, str):
        return "intencion_desconocida"

    texto_corregido = corregir_con_regex(texto, correcciones)
    texto_normalizado = unidecode(texto_corregido.lower())

    if any(saludo in texto_normalizado for saludo in SALUDOS):
        return "saludo"
    if any(despedida in texto_normalizado for despedida in DESPEDIDAS):
        return "despedida"
    if es_pregunta_envio(texto_normalizado): # Usar función específica para envíos
        return "pregunta_envio"
    if any(ayuda in texto_normalizado for ayuda in AYUDA):
        return "ayuda"

    return "intencion_desconocida" # Por defecto

def detectar_producto(texto):#23
    """Intenta detectar un tipo general de producto usando sinónimos."""
    texto_corregido = unidecode(corregir_con_regex(texto, correcciones).lower())
    for producto_base, lista_sinonimos in sinonimos_productos.items():
        if any(re.search(r'\b' + re.escape(s) + r'\b', texto_corregido) for s in lista_sinonimos):
            return producto_base
    return None

def detectar_pais_en_mensaje(mensaje):#24
    """Detecta si se menciona un país de la lista."""
    mensaje_lower = unidecode(mensaje.lower())
    for pais in PAISES:
        # Buscar palabra completa
        if re.search(r'\b' + re.escape(pais) + r'\b', mensaje_lower):
            return pais
    return None

def detectar_marca(texto):#25
    """Detecta si se menciona una marca de la lista."""
    texto_lower = unidecode(texto.lower())
    for marca in MARCAS:
        if re.search(r'\b' + re.escape(marca) + r'\b', texto_lower):
            return marca
    return None

# ========== FUNCIONES DE LÓGICA DEL CHATBOT ==========

def obtener_productos_desde_query(palabras_clave_query):#26
    """
    Busca productos en la BD basándose en las palabras clave.
    Intenta mapear a categorías y busca en nombre/descripción.
    """
    if not Product or not Product.objects: # Verificar si el modelo está disponible
        print("WARN: Modelo Product no disponible para búsqueda.")
        return Product.objects.none(), None # Devolver un queryset vacío

    query = palabras_clave_query.lower().strip()
    max_price = None # Inicializar max_price
    price_pattern = r'(?:menos de|bajo|maximo|hasta)\s*(\d+)\s*(k|mil)?'
    price_match = re.search(price_pattern, query)

    if price_match:
        price_value = int(price_match.group(1))
        multiplier = 1000 if price_match.group(2) in ['k', 'mil'] else 1
        max_price = price_value * multiplier
        # Remover la parte del precio de la query para no interferir con la búsqueda de keywords
        query = re.sub(price_pattern, '', query).strip()
        print(f"Detectado precio máximo: {max_price}")

    # Empezar con todos los productos disponibles
    products_query = Product.objects.filter(is_available=True)
    category_filter_applied = False
    keywords_used_for_filter = False

    # 1. Mapear keywords a categorías específicas
    keywords_in_query = query.split()
    found_category = None
    for keyword in keywords_in_query:
        if keyword in category_keywords and category_keywords[keyword]:
            category_name = category_keywords[keyword]
            try:
                # Usar get() asumiendo nombres de categoría únicos
                category = Category.objects.get(name__iexact=category_name)
                products_query = products_query.filter(category=category)
                category_filter_applied = True
                keywords_used_for_filter = True
                found_category = category_name
                print(f"Filtrado por categoría '{category_name}' debido a keyword '{keyword}'")
                # Romper si ya encontramos una categoría mapeada (o ajustar si pueden ser varias)
                break
            except Category.DoesNotExist:
                print(f"WARN: Categoría '{category_name}' mapeada pero no encontrada en BD.")
            except Category.MultipleObjectsReturned:
                 print(f"WARN: Múltiples categorías encontradas para '{category_name}'. Usando la primera.")
                 category = Category.objects.filter(name__iexact=category_name).first()
                 if category:
                    products_query = products_query.filter(category=category)
                    category_filter_applied = True
                    keywords_used_for_filter = True
                    found_category = category_name
                    break

    # 2. Filtrar por nombre/descripción/slug usando las palabras clave restantes
    search_keywords = [word for word in query.split() if len(word) >= 2] # Mínimo 2 caracteres
    if search_keywords:
        filter_q = Q()
        for keyword in search_keywords:
            # Buscar que CUALQUIERA (OR) de las palabras clave esté en estos campos
            filter_q |= Q(name__icontains=keyword) | \
                        Q(description__icontains=keyword) | \
                        Q(slug__icontains=keyword)

        # Aplicar el filtro Q
        products_query = products_query.filter(filter_q)
        keywords_used_for_filter = True
        print(f"Filtrado por keywords (OR) en nombre/desc/slug: {search_keywords}")

    # Si no se aplicó ningún filtro basado en keywords (raro), intentar con la query completa
    if not category_filter_applied and not keywords_used_for_filter and query:
         products_query = products_query.filter(Q(name__icontains=query) | Q(description__icontains=query))
         print(f"Filtrado general por query completa (fallback): {query}")

    # Aplicar filtro de precio si se detectó
    if max_price is not None:
        products_query = products_query.filter(price__lte=max_price)
        print(f"Aplicado filtro de precio: <= {max_price}")

    # Evitar duplicados y limitar resultados
    final_query = products_query.distinct().order_by('name')[:4]

    return final_query, max_price

def obtener_productos_desde_query_navbar(palabras_clave_query):#26

    if not Product or not Product.objects:
        print("WARN: Modelo Product no disponible para búsqueda.")
        return Product.objects.none(), None

    query = palabras_clave_query.lower().strip()
    max_price = None
    price_pattern = r'(?:menos de|bajo|maximo|hasta)\s*(\d+)\s*(k|mil)?'
    price_match = re.search(price_pattern, query)

    if price_match:
        price_value = int(price_match.group(1))
        multiplier = 1000 if price_match.group(2) in ['k', 'mil'] else 1
        max_price = price_value * multiplier
        query = re.sub(price_pattern, '', query).strip()
        print(f"Detectado precio máximo: {max_price}")

    products_query = Product.objects.filter(is_available=True)
    category_filter_applied = False
    keywords_used_for_filter = False

    keywords_in_query = query.split()
    found_category = None
    for keyword in keywords_in_query:
        if keyword in category_keywords and category_keywords[keyword]:
            category_name = category_keywords[keyword]
            try:
                category = Category.objects.get(name__iexact=category_name)
                products_query = products_query.filter(category=category)
                category_filter_applied = True
                keywords_used_for_filter = True
                found_category = category_name
                print(f"Filtrado por categoría '{category_name}' debido a keyword '{keyword}'")
                break
            except Category.DoesNotExist:
                print(f"WARN: Categoría '{category_name}' mapeada pero no encontrada en BD.")
            except Category.MultipleObjectsReturned:
                 print(f"WARN: Múltiples categorías encontradas para '{category_name}'. Usando la primera.")
                 category = Category.objects.filter(name__iexact=category_name).first()
                 if category:
                    products_query = products_query.filter(category=category)
                    category_filter_applied = True
                    keywords_used_for_filter = True
                    found_category = category_name
                    break

    search_keywords = [word for word in query.split() if len(word) >= 2] # Mínimo 2 caracteres
    if search_keywords:
        filter_q = Q()
        for keyword in search_keywords:
            filter_q |= Q(name__icontains=keyword) | \
                        Q(description__icontains=keyword) | \
                        Q(slug__icontains=keyword)

        products_query = products_query.filter(filter_q)
        keywords_used_for_filter = True
        print(f"Filtrado por keywords (OR) en nombre/desc/slug: {search_keywords}")

    if not category_filter_applied and not keywords_used_for_filter and query:
         products_query = products_query.filter(Q(name__icontains=query) | Q(description__icontains=query))
         print(f"Filtrado general por query completa (fallback): {query}")

    if max_price is not None:
        products_query = products_query.filter(price__lte=max_price)
        print(f"Aplicado filtro de precio: <= {max_price}")

    final_query = products_query.distinct().order_by('name')[:16]

    return final_query, max_price

def generar_respuesta_con_links(products, max_price=None):#27
    """Formatea la respuesta del chatbot con enlaces a los productos encontrados."""
    if not products.exists():
        # Este caso no debería ocurrir si se llama después de verificar products.exists()
        return "Lo siento, no encontré productos que coincidan."

    if max_price:
        # Formatear el precio para mostrarlo legible (ej: 500.000)
        price_formatted = '{:,.0f}'.format(max_price).replace(',', '.')
        response = f"Encontré estos productos por menos de ${price_formatted}:<br>"
    else:
        response = "He encontrado estos productos que podrían interesarte:<br>"

    # Construir la lista de productos con enlaces y precios
    for product in products:
        try:
            product_url = reverse('products:product_detail', args=[product.category.slug, product.slug])
            price_formatted = '{:,.0f}'.format(product.price).replace(',', '.')
            response += f"- <a href='{product_url}'>{product.name}</a> (${price_formatted})<br>"
        except Exception as e:
            print(f"Error al generar URL para producto {product.slug}: {e}")
            # Mostrar el producto sin enlace si falla la URL
            price_formatted = '{:,.0f}'.format(product.price).replace(',', '.')
            response += f"- {product.name} (${price_formatted}) [Error al generar enlace]<br>"

    if products.count() >= 5: # Si se alcanzó el límite de 5
        response += "<br>Estos son algunos resultados. Puedes ser más específico o usar la barra de búsqueda principal."

    return response

def responder_usuario(texto_corregido):  # 28 (Manejador Conversación Específica - Mejorado)
    """Maneja intenciones conversacionales básicas y predefinidas."""
    intencion = detectar_intencion(texto_corregido)
    # Requisito 3: Lenguaje Natural (Respuestas variadas)
    if intencion == "saludo":
        respuestas = ["¡Hola! 👋 Bienvenido a TecLegacy. ¿Qué buscas hoy?", "¡Qué tal! 😊 ¿En qué puedo ayudarte?",
                      "¡Buenas! Listo para ayudarte a encontrar lo mejor en tecnología.",
                      "¡Hola! Dime qué producto tienes en mente."]
        return random.choice(respuestas)
    elif intencion == "despedida":
        respuestas = ["¡Hasta luego! Gracias por visitarnos. Vuelve pronto 😊", "¡Chao! Que tengas un excelente día.",
                      "¡Nos vemos! Si necesitas algo más, aquí estaré.", "¡Adiós! Espero haberte ayudado."]
        return random.choice(respuestas)
    elif intencion == "ayuda":
        respuestas = [
            "Soy tu asistente virtual en TecLegacy. Puedo buscar productos, categorías o ayudarte con preguntas sobre envíos. ¿Qué necesitas?",
            "¡Claro! Pregúntame por un producto (ej: 'laptop gamer Asus') o sobre nuestros envíos (ej: 'envían a Medellín?').",
            "Estoy aquí para ayudarte. Dime qué buscas o si tienes dudas sobre envíos."]
        return random.choice(respuestas)
    elif intencion == "pregunta_envio":
        pais_detectado = detectar_pais_en_mensaje(texto_corregido)
        if pais_detectado and pais_detectado != "colombia":
            pais_title = pais_detectado.title()
            return f"Qué pena, por ahora nuestros envíos son sólo dentro de Colombia 🇨🇴. No podemos enviar a {pais_title}."
        else:
            # Asumir Colombia si no se especifica otro país
            return "¡Sí! Hacemos envíos a toda Colombia 🇨🇴. ¡Anímate a comprar! ✈️📦"
    # Se podría añadir manejo para 'chiste' u otras intenciones básicas aquí
    return None

# ========== VISTA PRINCIPAL DEL CHATBOT ==========

@csrf_exempt
def chatbot_query(request):#29
    """
    Vista principal que maneja las consultas del chatbot vía POST.
    Extrae palabras clave, busca productos/categorías, maneja intenciones,
    intenta conversación general con ChatterBot y genera fallback a búsqueda.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '').strip()

            if not query:
                return JsonResponse({'success': False, 'error': 'Consulta vacía.'})

            # 1. CORREGIR consulta
            query_corregida = corregir_con_regex(query, correcciones)

            # 2. EXTRAER PALABRAS CLAVE
            palabras_clave_str = extraer_palabras_clave(query_corregida)

            print(f"--- Consulta Recibida ---")
            print(f"Original: '{query}' -> Corregida: '{query_corregida}' -> Claves: '{palabras_clave_str}'")

            respuesta_encontrada = None
            respuesta_tipo = 'text'

            # 4. BUSCAR PRODUCTOS (usando palabras clave)
            if not respuesta_encontrada and palabras_clave_str:
                try:
                    productos_encontrados, max_price = obtener_productos_desde_query(palabras_clave_str)
                    if productos_encontrados and productos_encontrados.exists():
                        respuesta_encontrada = generar_respuesta_con_links(productos_encontrados, max_price)
                        respuesta_tipo = 'html'
                        print(f"Respuesta encontrada (Productos)")
                        return JsonResponse({'success': True, 'response': respuesta_encontrada, 'type': respuesta_tipo})
                except Exception as e_prod:
                     print(f"Error buscando productos: {e_prod}")

            # 5. BUSCAR CATEGORÍA EXACTA (usando palabras clave)
            if not respuesta_encontrada and palabras_clave_str and Category and Category.objects:
                try:
                    for category in Category.objects.all():
                        nombre_categoria_norm = unidecode(category.name.lower())
                        if palabras_clave_str == nombre_categoria_norm:
                            category_url = reverse("products:products_by_category", args=[category.slug])
                            respuesta_encontrada = f"Entendido. Aquí tienes la categoría <a href='{category_url}'>{category.name}</a>."
                            respuesta_tipo = 'html'
                            print(f"Respuesta encontrada (Categoría Exacta)")
                            return JsonResponse({'success': True, 'response': respuesta_encontrada, 'type': respuesta_tipo})
                except Exception as e_cat:
                    print(f"Error buscando categoría exacta: {e_cat}")

            # 6. MANEJAR INTENCIONES CONVERSACIONALES ESPECÍFICAS (ej: envío, saludo, despedida)
            if not respuesta_encontrada:
                respuesta_conversacional_especifica = responder_usuario(query_corregida) # Esta función SÓLO maneja cosas como envío, saludo, despedida, ayuda
                if respuesta_conversacional_especifica:
                    respuesta_encontrada = respuesta_conversacional_especifica
                    respuesta_tipo = 'text'
                    print(f"Respuesta encontrada (Conversacional Específica)")
                    return JsonResponse({'success': True, 'response': respuesta_encontrada, 'type': respuesta_tipo})

            # --- SI NADA DE LO ANTERIOR FUNCIONÓ ---

            # 7. INTENTAR CON CHATTERBOT PARA CONVERSACIÓN GENERAL (Usar query_corregida)
            if not respuesta_encontrada:
                try:
                    response_chatterbot = chatbot.get_response(query_corregida)

                    CONFIDENCE_THRESHOLD = 0.90
                    if response_chatterbot and response_chatterbot.confidence >= CONFIDENCE_THRESHOLD:
                        respuesta_encontrada = str(response_chatterbot)
                        respuesta_tipo = 'text'
                        print(f"Respuesta encontrada (ChatterBot General): Confianza {response_chatterbot.confidence:.2f}")
                        chatbot.learn_response(response_chatterbot, query_corregida) # Opcional: aprendizaje dinámico
                        return JsonResponse({'success': True, 'response': respuesta_encontrada, 'type': respuesta_tipo})
                    else:
                         confidence_val = response_chatterbot.confidence if response_chatterbot else 'N/A'
                         print(f"ChatterBot respondió con baja confianza ({confidence_val}). Ignorando respuesta general.")
                except Exception as e_cb:
                     print(f"Error al obtener respuesta de ChatterBot: {e_cb}")

            # 8. FALLBACK FINAL: Enlace a búsqueda general (usando palabras clave si existen)
            if not respuesta_encontrada:
                termino_busqueda_url = palabras_clave_str if palabras_clave_str else query_corregida
                if not termino_busqueda_url: termino_busqueda_url = query
                try:
                    search_url = f"{reverse('products:search')}?q={quote_plus(termino_busqueda_url)}"
                    respuesta_fallback = (
                        f"No encontré una respuesta directa para '{query}'.<br>"
                        f"Puedes <a href='{search_url}'>buscar '{termino_busqueda_url}' en toda la tienda</a> "
                        f"o intentar reformular tu pregunta."
                    )
                    respuesta_encontrada = respuesta_fallback
                    respuesta_tipo = 'html'
                    guardar_pregunta_desconocida(query)
                    print(f"Respuesta (Fallback a Búsqueda)")
                    return JsonResponse({'success': True, 'response': respuesta_encontrada, 'type': respuesta_tipo})
                except Exception as e_search:
                    print(f"Error crítico generando URL de búsqueda: {e_search}")
                    respuesta_error_final = "Lo siento, tuve problemas para procesar tu solicitud. Por favor, intenta buscar manualmente."
                    guardar_pregunta_desconocida(f"{query} [ERROR FALLBACK]")
                    return JsonResponse({'success': True, 'response': respuesta_error_final, 'type': 'text'})

            # Seguridad por si acaso
            print("WARN: Se alcanzó el final de chatbot_query sin devolver respuesta.")
            return JsonResponse({'success': False, 'error': 'Flujo de respuesta incompleto.'})

        # ... (Manejo de excepciones JSONDecodeError y Exception general sin cambios) ...
        except json.JSONDecodeError:
             print("Error: Recibido JSON inválido.")
             return JsonResponse({'success': False, 'error': 'Error decodificando JSON.'}, status=400)
        except Exception as e:
            print(f"ERROR INESPERADO en chatbot_query: {str(e)}\n{traceback.format_exc()}")
            return JsonResponse({'success': False, 'error': 'Ha ocurrido un error interno en el servidor.'}, status=500)

    return JsonResponse({'success': False, 'error': 'Método no permitido. Usa POST.'}, status=405)

def responder_chatbot(request):#30
    if request.method == "POST":
        mensaje_usuario = request.POST.get("message", "")
        respuesta = chatbot_instance.get_response(mensaje_usuario)
        return JsonResponse({"response": str(respuesta)})

def train_bot_view(request):
     # Lógica para (re)entrenar el bot si es necesario
     pass

# =========== NavBar ================

@csrf_exempt
def chatbot_search(request):
    if request.method == 'POST':
        try:
            # Cambia esto para recibir JSON correctamente
            data = json.loads(request.body)
            query = data.get('query', '')

            # Usa tus funciones existentes
            query_corregida = corregir_con_regex(query, correcciones)
            palabras_clave = extraer_palabras_clave(query_corregida)
            productos, _ = obtener_productos_desde_query_navbar(palabras_clave)

            results = []
            for p in productos[:15]:
                try:
                    results.append({
                        "name": p.name,
                        "price": float(p.price),  # Asegurar que es número
                        "image": p.image.url if p.image else "/static/images/default-product.png",
                        "url": reverse('products:product_detail', args=[p.category.slug, p.slug]),
                        "category": p.category.name
                    })
                except Exception as e:
                    print(f"Error procesando producto {p.id}: {str(e)}")
                    continue

            return JsonResponse({
                "success": True,
                "query": query,
                "products": results
            })

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "JSON inválido"}, status=400)
        except Exception as e:
            print(f"Error en chatbot_search: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)