from django.shortcuts import render, get_object_or_404
from chatbot.views import corregir_con_regex, extraer_palabras_clave, obtener_productos_desde_query
from chatbot.views import correcciones, PALABRAS_A_IGNORAR, category_keywords,MARCAS,BUSQUEDA_TRIGGERS,detectar_intencion,INTENCIONES,PRODUCTOS,sinonimos_productos,category_keywords
from django.core.paginator import Paginator
from chatbot.views import extraer_palabras_clave
from .models import Category, Product
from django.db import models
import re

def index(request):
    """Vista de la página principal con productos destacados."""
    featured_products = Product.objects.filter(is_featured=True, is_available=True)[:8]
    categories = Category.objects.filter(is_active=True)[:6]

    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'products/index.html', context)


def product_list(request, category_slug=None):
    """Lista de productos, puede filtrarse por categoría."""
    category = None
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(is_available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=category)

    # Paginación: 12 productos por página
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    context = {
        'category': category,
        'categories': categories,
        'products': products_page,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, category_slug, product_slug):
    """Detalle de un producto específico."""
    product = get_object_or_404(
        Product,
        slug=product_slug,
        category__slug=category_slug,
        is_available=True
    )

    # Productos relacionados: misma categoría, excepto el actual
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)

def search_products(request):
    query_original = request.GET.get('q', '').strip()
    productos = []
    mostrar_mensaje_no_encontrado = False  # Flag para controlar el mensaje

    if query_original:
        # PASO 1: Procesar la consulta con la lógica inteligente
        query_corregida = corregir_con_regex(query_original,
                                             correcciones)  # Asegúrate de tener 'correcciones' accesible
        palabras_clave = extraer_palabras_clave(
            query_corregida)  # Asegúrate de tener 'extraer_palabras_clave' y sus dependencias accesibles

        print(f"Búsqueda en página completa: Original='{query_original}', Procesada='{palabras_clave}'")

        productos_encontrados, _ = obtener_productos_desde_query(palabras_clave)

        productos = productos_encontrados  # Usamos los resultados de la búsqueda inteligente

        if not productos.exists():  # Verificar si el queryset está vacío
            mostrar_mensaje_no_encontrado = True  # No se encontraron productos con la lógica inteligente

    else:
        # Si la consulta original estaba vacía
        mostrar_mensaje_no_encontrado = True

    context = {
        'query': query_original,  # Mostrar la consulta original al usuario
        'products': productos,
        'mostrar_mensaje_no_encontrado': mostrar_mensaje_no_encontrado,
        'categories': Category.objects.all(),
    }
    # Asegúrate de que esta plantilla sea la que muestra la página que viste ("Resultados de búsqueda...")
    return render(request, 'products/search_results.html', context)
