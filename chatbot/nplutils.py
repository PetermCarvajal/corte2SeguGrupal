import re
import spacy
from spacy.lang.es.stop_words import STOP_WORDS
import unicodedata
from unidecode import unidecode



from collections import defaultdict

# Cargar modelo de lenguaje español
try:
    nlp = spacy.load("es_core_news_sm")
except:
    import es_core_news_sm

    nlp = es_core_news_sm.load()

correcciones ={
    "ke":"que",
    "k":"que",
    "xq":"por que",
    "pa":"para",
    "tbn":"también",
    "toy":"estoy",
    "toi":"estoy",
    "dnd":"donde",
    "kiero":"quiero",
    "sta":"esta",
    "stoy":"estoy",
    "ntnc":"entonces",
    "q tal":"qué tal",
     "teclado mecaniko": "teclado mecánico",
    "teclado mecanico": "teclado mecánico",
    "raton": "ratón",
    "mouse gamer": "ratón gamer",
    "monitor curvo": "monitor curvo",
    "pantaya": "pantalla",
    "pantaya gamer": "pantalla gamer",
    "grafica": "tarjeta gráfica",
    "grafika": "tarjeta gráfica",
    "placa madre": "placa base",
    "board": "placa base",
    "motherboard": "placa base",
    "memoria ram": "RAM",
    "almacenamiento ssd": "disco SSD",
    "almacenamiento hdd": "disco HDD",
    "gabinete gamer": "torre gamer",
    "case": "torre",
    "fuente poder": "fuente de poder",
    "fuente": "fuente de poder",
    "ventilador rgb": "ventilador RGB",
    "cooler": "disipador",
    "silla gammer": "silla gamer",
    "silla gamer": "silla gamer",
    "escritorio gamer": "mesa gamer",
    "control play": "control de PlayStation",
    "control xbox": "control de Xbox",
    "xbox x": "Xbox Series X",
    "xbox s": "Xbox Series S",
    "ps5": "PlayStation 5",
    "ps4": "PlayStation 4",
    "nintendo switch": "Nintendo Switch",
    "switch oled": "Nintendo Switch OLED",
    "switch lite": "Nintendo Switch Lite",
    "minecra": "Minecraft",
    "mincraf": "Minecraft",
    "micraf": "Minecraft",
    "fortnait": "Fortnite",
    "fornite": "Fortnite",
    "jueguitos": "videojuegos",
    "jueguito": "videojuego",
    "play": "PlayStation",
    "usb": "memoria USB",
    "micro sd": "tarjeta MicroSD",
    "auris": "auriculares",
    "cargador cel": "cargador de celular",
    "cargador lap": "cargador de laptop",
    "lap": "laptop",
    "pc gamer": "PC Gamer",
    "notebook": "laptop",
    "cpu": "procesador",
    "gpu": "tarjeta gráfica",
    "ssd": "disco SSD",
    "hdd": "disco HDD",
    "cámara": "cámara web",
    "camara": "cámara",
    "porq": "porque",
    "xk": "porque",
    "pq": "porque",
    "asi que": "así que",
    "nose": "no sé",
    "aunqueh": "aunque",
    "en tonces": "entonces",
    "tonces": "entonces",
    "entonses": "entonces",
    "dsp": "después",
    "luegp": "luego",
    "depues": "después",
    "ademas": "además",
    "aparte de eso": "además",
    "por lo tanto": "por lo tanto",
    "asi ": "asimismo",
    "por otro lado": "por otro lado",
    "en cambio": "en cambio",
    "tal vez": "tal vez",
    "de hecho": "de hecho",
    "aci que": "así que",
    "noc": "no sé",
    "noce": "no sé",
    "aun que": "aunque",
    "anque": "aunque",
    "desp": "después",
    "despue": "después",
    "de mas": "además",
    "admas": "además",
    "sinembargo": "sin embargo",
    "sin enbargo": "sin embargo",
    "sin en vargo": "sin embargo",
    "porlo tanto": "por lo tanto",
    "por lo tnto": "por lo tanto",
    "por lotanto": "por lo tanto",
    "asi mismo": "asimismo",
    "así mismo": "asimismo",
    "asi mismoo": "asimismo",
    "por consiguiente": "por consiguiente",
    "por consiquiente": "por consiguiente",
    "por consigiente": "por consiguiente",
    "en conclusion": "en conclusión",
    "conclucion": "conclusión",
    "en conclución": "en conclusión",
    "en resumen": "en resumen",
    "resumiendo": "en resumen",
    "por ejemplo": "por ejemplo",
    "xej": "por ejemplo",
    "ejem": "por ejemplo",
    "en fin": "en fin",
    "enfin": "en fin",
    "al final": "al final",
    "alfinal": "al final",
    "es decir": "es decir",
    "osea": "o sea",
    "ose": "o sea",
    "o sea": "o sea",
    "talvez": "tal vez",
    "tal ves": "tal vez",
    "talves": "tal vez",
    "quizas": "quizás",
    "quiza": "quizá",
    "kizas": "quizás",
    "kisa": "quizá",
    "deecho": "de hecho",
    "de echo": "de hecho",
    "valla": "vaya",
    "vaya": "vaya",
    "vaya a": "vaya a",
    "tenga": "tenga",
    "que tenga": "que tenga",
    "un": "un",
    "una": "una",
    "unos": "unos",
    "unas": "unas",
    "con": "con",
    "i": "y",
    "u":"u",
    "por ke": "porque",
    "ya qe": "ya que",
    "ya ke": "ya que",
    "yaque": "ya que",
    "pues": "pues",
    "puez": "pues",
    "puesto qe": "puesto que",
    "puesto ke": "puesto que",
    "puesto que": "puesto que",
    "dado qe": "dado que",
    "dado ke": "dado que",
    "dado que": "dado que",
    "debido a que": "debido a que",
    "debuidoi a q": "debido a que",
    "x eso": "por eso",
    "por eso": "por eso",
    "por eso mismo": "por eso mismo",
    "x":"por",
    "mejor dicho": "mejor dicho",
    "en otras palabras": "en otras palabras",
    "vale decir": "vale decir",
    "esto es": "esto es",
    "estoes": "esto es",
    "mejor dixo": "mejor dicho",
    "es dcir": "es decir",
    "en primer lugar": "en primer lugar",
    "primeramente": "primeramente",
    "segundo": "segundo",
    "en segundo lugar": "en segundo lugar",
    "por último": "por último",
    "finalmente": "finalmente",
    "para terminar": "para terminar",
    "para concluir": "para concluir",
    "en conclucion": "en conclusión",
    "enconclusion": "en conclusión",
    "hbaer":"a ver",
    "haber":"a ver",
    "alla":"haya",
    "aserca": "acerca",
    "aser": "hacer",
    "aserlo": "hacerlo",
    "aver": "a ver",
    "abeses": "a veces",
    "avesez": "a veces",
    "ahy": "hay",
    "ahi": "ahí",
    "hay": "hay",
    "ay": "hay",
    "ahy que": "hay que",
    "ay que": "hay que",
    "oi": "hoy",
    "oi dia": "hoy día",
    "oir": "oír",
    "toa": "toda",
    "to": "todo",
    "na": "nada",
    "q onda": "qué onda",
    "holi": "hola",
    "aki": "aquí",
    "aki toy": "aquí estoy",
    "toy bn": "estoy bien",
    "bn": "bien",
    "bno": "bueno",
    "klk": "¿qué tal?",
    "procesador amd": "procesador AMD",
    "intel i5": "Intel i5",
    "intel i7": "Intel i7",
    "grafica nvidia": "tarjeta gráfica NVIDIA",
    "grafica amd": "tarjeta gráfica AMD",
    "disco duro externo": "HDD externo",
    "memoria externa": "almacenamiento externo",
    "microfon": "micrófono",
    "micro": "micrófono",
    "cascos": "audífonos",
    "auris gamer": "auriculares gamer",
    "headset": "auriculares con micrófono",
    "lsta":"lista",
    "articulso":"articulos",
    "lapto":"laptop",
    "laotop":"laptop",
    "compu":"computador",
    "cel":"celular",
    "celu":"celular",

}

sinonimos_productos = {

    "celular": ["teléfono","móvil","smartphone","teléfono móvil","dispositivo móvil"],
    "tv": ["televisor", "pantalla", "television"],
    "pc": ["computadora","computador","ordenador","computadora de escritorio","computador de escritorio","ordenador de mesa","pc de escritorio","equipo de escritorio"],    # ... (agrega más según necesites)
    "laptop": ["notebook", "portátil", "ordenador portátil", "computadora portátil", "computador portátil"],
    "monitor": ["pantalla", "display", "monitor de computadora", "monitor de pc", "monitor gamer", "pantalla gamer"],
    "ratón": ["mouse", "ratón gamer", "mouse gamer", "control de pc", "puntero"],
    "teclado": ["teclado gamer","teclado mecánico","teclado inalámbrico","keyboard"],
    "auriculares": ["audífonos", "auris", "cascos", "headset", "auriculares gamer", "audífonos gamer", "auriculares con micrófono"],
    "juegos":["video juegos","jueguitos","juegazos"]

}


def preprocesar_texto(texto):
    """
    info Limpia y normaliza texto (opcional si se desea pasar por NLP antes del modelo).
    """
    texto = unidecode(texto.lower())
    texto = re.sub(r'[^\w\s]', '', texto)  # remover puntuación
    doc = nlp(texto)
    return [token.lemma_ for token in doc if not token.is_stop and len(token.text) > 2]


def corregir_texto(texto):
    """
    info Aplica correcciones básicas y reemplazos de jerga para mejorar comprensión del modelo.
    """
    texto = texto.lower()
    for error, correccion in correcciones.items():
        texto = re.sub(r'\b' + re.escape(error) + r'\b', correccion, texto)
    return texto

def corregir_con_regex(texto, correcciones):
    """Corrección más avanzada con regex"""
    patron = re.compile(r'\b(' + '|'.join(re.escape(k) for k in correcciones.keys()) + r')\b')
    return patron.sub(lambda x: correcciones[x.group()], texto.lower())

def filtrar_stopwords(texto):
    """
    info Elimina palabras vacías (puede ayudar a analizar texto o mostrar resúmenes).
    """
    return ' '.join([p for p in texto.split() if p not in STOP_WORDS])

def detectar_intencion(texto):
               texto_corregido = corregir_texto(texto)
               texto_preprocesado = ' '.join(preprocesar_texto(texto_corregido))

               # Intenciones básicas con regex o palabras clave
               if re.search(r'\b(hola|buenas|ola|klk|holi)\b', texto_corregido):
                   return "saludo"
               if re.search(r'\b(adios|chao|nos vemos|bye)\b', texto_corregido):
                   return "despedida"
               if re.search(r'\b(tienen|quiero|busco|venden|hay|tienen envio)\b', texto_corregido):
                   return "pregunta_producto"
               if re.search(r'\b(precio|cuesta|vale|cuánto)\b', texto_corregido):
                   return "pregunta_precio"
               if re.search(r'\b(envio|envían|mandan|llegan)\b', texto_corregido):
                   return "pregunta_envio"
               if re.search(r'\b(jajaja|xd|wtf|lol)\b', texto_corregido):
                   return "chiste"
               return "intencion_desconocida"

def detectar_producto(texto):
    texto_corregido = corregir_texto(texto)
    for producto, sinonimos in sinonimos_productos.items():
        for s in sinonimos:
            if re.search(r'\b' + re.escape(s) + r'\b', texto_corregido):
                return producto
    return None

def responder_usuario(texto):
    intencion = detectar_intencion(texto)
    producto = detectar_producto(texto)

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
        return "Sí, realizamos envíos a todo el país 🚚. ¿A qué ciudad te interesa el envío?"
    elif intencion == "chiste":
        return "Jajaja 😂 ¡Tú sí que sabes bromear! Pero también sé de hardware si necesitas ayuda 😎"
    else:
        return "No estoy seguro de haber entendido bien 🤔. ¿Puedes decirlo de otra manera?"