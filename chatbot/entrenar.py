from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import os

# Ruta absoluta hacia chatbot_db.sqlite3 dentro de la carpeta /chatbot
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'chatbot_db.sqlite3')

chatbot = ChatBot(
    "CL4P-TP",
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri=f'sqlite:///{db_path}'
)

trainer = ListTrainer(chatbot)

trainer.train([
    "Hola",
    "Hola, ¿en qué puedo ayudarte?",
    "¿Cuál es tu nombre?",
    "Me llamo CL4P-TP, ¡tu asistente! en <b>Teclegacy</b>",
])

faq = {
    "envios": {
        "¿Hacen envíos?": "Sí, hacemos envíos a toda Colombia.",
        "¿Cuánto tarda el envío?": "El tiempo de envío depende de tu ciudad. Generalmente entre 2 a 5 días hábiles.",
        "¿Se puede hacer seguimiento del pedido?": "¡Claro! Una vez que tu pedido es despachado, te enviamos un número de guía para que puedas hacer el seguimiento en línea.",
        "¿Envían a Bogotá?": "Sí, enviamos a Bogotá y a toda Colombia.",
        "¿Cuánto cuesta el envío?": "El costo del envío varía según tu ubicación y el método de pago. Se calcula automáticamente al momento de pagar.",
        "¿Puedo hacer seguimiento de mi pedido?": "¡Claro! Una vez que tu pedido sea despachado, recibirás un número de guía para que puedas hacer el seguimiento online.",
        "¿Puedo retirar en tienda o punto físico?": "Sí, si estás en Armenia, podés coordinar con nosotros para retiro en punto físico. Escríbenos por WhatsApp para más detalles."
    },

    "productos": {
        "¿Qué venden?": "En la Tienda <b>Teclegacy</b> Puedes Encontrar los Siguientes Productos:Celulares, Tablets,Coleccionables,Componentes Eléctronicos para Computador,Consolas de Video Juegos,Video Juegos,Accesorios para Tu Set Up y Streaming",
        "¿Tienen un catálogo?": "¡Sí! Disponemos de un catálogo en continua expansión que podés revisar desde nuestra página 'Productos'.",
        "Quiero ver el Catálogo":"Puedes encontrar los Productos en el botón 'Productos', Ubicado en la Parte Superior de la Página",
        "¿Dónde está la Búsqueda?":"Puedes Hacer Búsqueda de Productos Mediante la Barra de Búsqueda, que Tienes en la Parte Superior de la Página. Fácilmente reconocible por la Lupa 🔍",
        "¿Tienen garantía?":"¡Claro!, Siempre que este dentro de las politicas",
        "¿Cuáles son las politcas de Garantía":"Para que la Garantia sea aplicable el producto debe de tener:\n1. Daños Por Defecto de Fabrica. \n2. No tener daños por Mal uso.\n3. Debe devolverse en la Caja o empaque Original con todo lo que trae \n4. Escribirnos al whatsapp el motivo y las pruebas de Estado del producto."
    },
    "informacion_tienda": {
        "¿Cuál es el horario de atención?": "Nuestro horario de atención es de lunes a sábado de 9:00 a.m. a 6:00 p.m.",
        "¿Dónde están ubicados?": "Actualmente operamos de forma online. Nuestro centro logístico está en Armenia.",
        "¿Ofrecen descuentos o promociones?":"¡Por Supuesto!, aleatoriamente se reparte cupones de Descuento",
        "¿Tienen atención al cliente por WhatsApp?": "¡Sí! Podés escribirnos directamente a nuestro WhatsApp para recibir ayuda personalizada.",
    },

    "funcionamiento_web": {
        "¿Cómo hago un pedido?": "Solo tenés que ir al producto que querés, hacer clic en 'Agregar al carrito' y seguir los pasos de compra.",
        "¿No puedo completar la compra, qué hago?": "Si estás teniendo problemas, escribinos por WhatsApp y con gusto te ayudamos a finalizar tu compra.",
        "¿Cómo uso un cupón de descuento?": "En el paso de pago hay un campo que dice 'Código de descuento',lo ingresás antes de pagar y se aplicará automaticamente.",
        "¿Qué servicios Brindan?":"Nuestra Tienda consta de un Único Servicio: Venta de Productos, poseemos una considerable y creciente cantidad de productos",
    },

    "categorias": {
        "¿Qué categorías manejan?": "Manejamos las siguientes categorías: celulares, tablets, accesorios gamer, consolas, componentes y coleccionables."
    },

    "cuenta_usuario": {
        "¿Cómo creo una cuenta?": "Hacé clic en 'Iniciar sesión' > 'Registrarse', completá tus datos ¡y listo!",
        "¿Olvidé mi contraseña, qué hago?": "En la pantalla de inicio de sesión, hacé clic en '¿Olvidaste tu contraseña?' y seguí las instrucciones.",
        "¿Cómo actualizo mis datos personales?": "Desde tu perfil podés editar tu información personal, dirección de envío, etc."
    },

    "bot": {
        "¿Cuál es tu nombre?": "Soy el modelo CL4P-TP, mejor conocido como 'Juanjo'; tu asistente virtual.",
        "¿Quién eres?": "Soy el modelo CL4P-TP, mejor conocido como 'Juanjo'; tu asistente virtual.",
        "Dime tu nombre":"Soy el modelo CL4P-TP, mejor conocido como 'Juanjo'; tu asistente virtual.",
        "¿Cómo te dicen?":"Soy el modelo CL4P-TP, Mejor conocido como 'Juanjo'; tu asistente virtual.",
        "¿Quién te programó?": "Fui programado por Carvajal Lugo Peter Manolo.",
        "¿Quien creo Todo esto?":"Todo lo que ves Aca fue Creado por Johan , Peter y Nicolas",
        "¿Puedo hablar con un humano?": "Claro, si necesitás ayuda directa, podés escribir a nuestro WhatsApp y un asesor te atenderá.",
        "¿Para qué sirve este asistente?": "Soy tu guía para ayudarte a encontrar productos, resolver dudas frecuentes y brindarte soporte.",
        "¿Cómo puedo dejar un comentario o sugerencia?": "Podés enviarnos tu comentario desde la sección de contacto o directamente por WhatsApp."
    },

    "pqr": {
        "¿Puedo cambiar un producto?": "Sí, podés hacer cambios siempre que el producto esté sin uso y en su empaque original.",
        "¿Cuál es la política de devoluciones?": "Podés devolver un producto dentro de los primeros 5 días hábiles desde que lo recibís. Revisá nuestras políticas en la web.",
        "¿Dónde puedo ver el Precio del producto?":"Los precios de los productos pueden encontrar en la misma información del mismo",
        "¿Qué métodos de Pago Reciben?":"Recibimos los Siguientes Métodos de Pago Efectivo o Tarjeta: Mercado Pago, Nequí,Paypal,PayU y Wompi",
        "¿Se puede pagar en cuotas?": "Sí, aceptamos pagos en cuotas con tarjetas de crédito a través de nuestras pasarelas de pago como PayU, Wompi o MercadoPago.",
        "¿Es seguro comprar por esta web?": "Sí, utilizamos plataformas de pago certificadas y tu información está protegida por protocolos de seguridad.",
        "¿Hacen facturas?": "Sí, si necesitás factura, puedés solicitarla al momento de hacer tu pedido o escribiéndonos por WhatsApp con el mismo código de seguimiento del producto.",
        "¿Qué hago si recibí un producto defectuoso?": "Lamentamos mucho eso 😔. Por favor, contáctanos con fotos del producto y tu número de pedido para darte una solución rápida.",
    }
}

# Diccionario de variantes
variantes = {
    "¿Envían a Bogotá?": "¿Hacen envíos?",
    "¿A qué zonas hacen envios?":"¿Hacen envíos?",
    "¿Puedo rastrear el pedido?": "¿Se puede hacer seguimiento del pedido?",
    "¿Qué hay en la tienda?": "¿Qué productos tienen?",
    "¿Qué artículos tienen?": "¿Qué productos tienen?",
    "¿Qué cosas venden?": "¿Qué productos tienen?",
    "¿Tienen una lista de productos?": "¿Tienen un catálogo?",
    "¿Dónde están?": "¿Dónde están ubicados?",
    "¿Dónde se encuentran?": "¿Dónde están ubicados?",
    "¿Puedo comprar en la web?": "¿Cómo hago un pedido?",
    "¿No puedo comprar?": "¿No puedo completar la compra, qué hago?",
    "¿Cómo ingreso un código de descuento?": "¿Cómo uso un cupón de descuento?",
    "¿Cómo me registro?": "¿Cómo creo una cuenta?",
    "Olvidé mi clave": "¿Olvidé mi contraseña, qué hago?",
    "¿Cuál es tu apodo?": "¿Cuál es tu nombre?",
    "¿Cómo te llamas?": "¿Cuál es tu nombre?",
    "¿Quién te desarrolló?": "¿Quién te programó?",
    "¿Quienes Hicieron esto?":"¿Quien creo Todo esto?",
    "¿Cuántas personas Hicieron esto":"¿Quien creo Todo esto?",
    "¿Quiénes desarrollaron esto?":"¿Quien creo Todo esto?",
    "¿Que Productos hay en la Tinda?":"¿Qué Venden?",
    "¿Qué Venden en la Tienda?":"¿Qué Venden?",
    "¿Qué Tienen a la Venta?":"¿Qué Venden?",
    "¿Dónde están los productos?":"Quiero ver el catálogo",
    "¿Cómo veo los productos?":"Quiero ver el catálogo",
    "¿Dónde están los artículos?":"Quiero ver el catálogo",
    "Enséñame los productos":"Quiero ver el catálogo",
    "Muéstrame los productos":"Quiero ver el catálogo",
    "¿Dónde puedo revisar los productos disponibles?":"Quiero ver el catálogo",
    "¿Cómo accedo a los productos?":"Quiero ver el catálogo",
    "¿Dónde busco productos?": "¿Dónde está la búsqueda?",
    "¿Cómo encuentro algo en la tienda?": "¿Dónde está la búsqueda?",
    "¿Cómo puedo buscar lo que quiero?": "¿Dónde está la búsqueda?",
    "¿Cómo localizo un producto?": "¿Dónde está la búsqueda?",
    "Quiero buscar un artículo": "¿Dónde está la búsqueda?",
    "¿Cómo se usa el buscador?": "¿Dónde está la búsqueda?",
    "¿Qué tienen para vender?":"¿Qué Venden?",
    "¿Qué artículos ofrecen?":"¿Qué Venden?",
    "¿Qué hay en su catálogo?":"¿Qué Venden?",
    "¿Qué productos tienen?":"¿Qué Venden?",
    "¿Qué mercancía manejan?":"¿Qué Venden?",
    "¿Qué venden ustedes?":"¿Qué Venden?",
    "¿Qué encuentro en la tienda?":"¿Qué Venden?",
    "¿Qué servicios Ofrecen?":"¿Qué Servicios brindan?",
    "¿Qué tipo de servicios tienen disponibles?":"¿Qué Servicios brindan?",
    "¿Qué prestaciones brindan?":"¿Qué Servicios brindan?",
    "¿Qué soluciones ofrecen?":"¿Qué Servicios brindan?",
    "¿Qué opciones tienen para los clientes?":"¿Qué Servicios brindan?",
    "Qué servicios forman parte de su catálogo?":"¿Qué Servicios brindan?",
    "¿Qué productos y servicios están a disposición?":"¿Qué Servicios brindan?",
    "¿Qué asistencia proporcionan?":"¿Qué Servicios brindan?",
    "¿Qué ofrecen al público?":"¿Qué Servicios brindan?",
    "¿Qué servicios están en su portafolio?":"¿Qué Servicios brindan?",
    "¿Disponen de un listado de productos?":"¿Tienen un catálogo?",
    "¿Ofrecen una guía o catálogo con sus artículos?":"¿Tienen un catálogo?",
    "¿Tienen una lista de los servicios y productos disponibles?":"¿Tienen un catálogo?",
    "¿Cuentan con un inventario detallado para consultar?":"¿Tienen un catálogo?",
    "¿Es posible acceder a su catálogo de opciones?":"¿Tienen un catálogo?",
    "¿Dónde puedo ver los precios?":"¿Dónde puedo ver el Precio del producto?",
    "¿Dónde puedo encontrar información sobre los precios?":"¿Dónde puedo ver el Precio del producto?",
    "¿Puedo ver los precios en algún lugar?":"¿Dónde puedo ver el Precio del producto?",
    "¿Tienen un listado o catálogo con los precios disponibles?":"¿Dónde puedo ver el Precio del producto?",
    "¿Dónde está la información de costos de sus productos o servicios?":"¿Dónde puedo ver el Precio del producto?",
    "¿Cuánto demora en llegar el pedido?":"¿Cuánto tarda el envío?",
}

for categoria, preguntas_respuestas in faq.items():
    for pregunta, respuesta in preguntas_respuestas.items():
        trainer.train([pregunta, respuesta])

        # Si hay variantes de esta pregunta, entrenarlas también
        for variante, original in variantes.items():
            if original == pregunta:
                trainer.train([variante, respuesta])