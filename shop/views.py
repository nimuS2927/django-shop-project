from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django.views.generic import View

from shop.basket import SessionBasket
from shop.forms import CategoryForm
from shop.forms import ImageCategoryForm
from shop.forms import ImageProductForm
from shop.forms import ProductForm
from shop.forms import ProductSearchForm
from shop.forms import PromotionForm
from shop.forms import TagForm
from shop.models import Category
from shop.models import ImageCategory
from shop.models import ImageProduct
from shop.models import Order
from shop.models import OrderItem
from shop.models import Product
from shop.models import Promotion
from shop.models import Tag


class StartPageView(TemplateView):
    template_name = "shop/start_page.html"


class CategoryListView(ListView):
    """Список всех категорий с древовидной структурой"""

    model = Category
    template_name = "shop/category_list.html"
    context_object_name = "categories"
    paginate_by = 20

    def get_queryset(self):
        return Category.objects.filter(parent=None).prefetch_related(
            "children", "image"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Категории товаров"
        return context


class CategoryDetailView(DetailView):
    """Детальная информация о категории с товарами"""

    model = Category
    template_name = "shop/category_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()

        # Получаем товары категории с пагинацией
        products = (
            Product.objects.filter(category=category)
            .select_related("category")
            .prefetch_related("images", "tags")
        )
        paginator = Paginator(products, 12)
        page_number = self.request.GET.get("page")
        context["products"] = paginator.get_page(page_number)

        # Получаем подкатегории
        context["subcategories"] = category.get_children()

        context["title"] = f"Категория: {category.title}"
        return context


class CategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Создание новой категории"""

    model = Category
    form_class = CategoryForm
    template_name = "shop/category_form.html"
    success_url = reverse_lazy("shop:category_list")
    success_message = "Категория успешно создана"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Создать категорию"
        return context


class CategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Редактирование категории"""

    model = Category
    form_class = CategoryForm
    template_name = "shop/category_form.html"
    success_url = reverse_lazy("shop:category_list")
    success_message = "Категория успешно обновлена"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Редактировать категорию: {self.object.title}"
        return context


class CategoryDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Удаление категории"""

    model = Category
    template_name = "shop/category_confirm_delete.html"
    success_url = reverse_lazy("shop:category_list")
    success_message = "Категория успешно удалена"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Удалить категорию: {self.object.title}"
        return context


class ProductListView(ListView):
    """Список всех товаров с фильтрацией и поиском"""

    model = Product
    template_name = "shop/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.select_related("category").prefetch_related(
            "images", "tags", "promotions"
        )

        # Фильтрация по категории
        category_id = self.request.GET.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Фильтрация по доступности
        available = self.request.GET.get("available")
        if available == "true":
            queryset = queryset.filter(available=True)
        elif available == "false":
            queryset = queryset.filter(available=False)

        # Поиск по названию и описанию
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        # Фильтрация по цене
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Фильтрация по тегам
        tag_id = self.request.GET.get("tag")
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Каталог товаров"
        context["search_form"] = ProductSearchForm(self.request.GET)
        return context


class ProductDetailView(DetailView):
    """Детальная информация о товаре"""

    model = Product
    template_name = "shop/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.select_related("category").prefetch_related(
            "images", "tags", "promotions"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context["title"] = product.title
        context["related_products"] = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:4]
        return context


class ProductCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Создание нового товара"""

    model = Product
    form_class = ProductForm
    template_name = "shop/product_form.html"
    success_url = reverse_lazy("shop:product_list")
    success_message = "Товар успешно создан"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Создать товар"
        return context


class ProductUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Редактирование товара"""

    model = Product
    form_class = ProductForm
    template_name = "shop/product_form.html"
    success_url = reverse_lazy("shop:product_list")
    success_message = "Товар успешно обновлен"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Редактировать товар: {self.object.title}"
        return context


class ProductDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Удаление товара"""

    model = Product
    template_name = "shop/product_confirm_delete.html"
    success_url = reverse_lazy("shop:product_list")
    success_message = "Товар успешно удален"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Удалить товар: {self.object.title}"
        return context


class BasketView(TemplateView):
    """Корзина пользователя"""

    template_name = "shop/basket.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        basket = SessionBasket(self.request)

        # Превращаем корзину в список элементов для шаблона
        basket_items = []
        for item in basket:
            product = item["product"]
            basket_items.append(
                {
                    "pk": product.pk,
                    "product": product,
                    "count": item["count"],
                    "price": product.price,
                    "total_price": product.price * item["count"],
                }
            )

        context["basket_items"] = basket_items
        context["basket"] = {
            "total_cost": sum(item["total_price"] for item in basket_items),
            "basket_count": sum(item["count"] for item in basket_items),
        }
        context["title"] = "Корзина"
        return context


@method_decorator(require_POST, name="dispatch")
class AddToBasketView(View):
    """Добавление товара в корзину"""

    def post(self, request, product_id):
        basket = SessionBasket(request)
        product = get_object_or_404(Product, id=product_id)

        if not product.available:
            return JsonResponse({"success": False, "message": "Товар недоступен"})

        basket.add(product)

        total_cost = sum(
            Decimal(item["price"]) * item["count"] for item in basket.basket.values()
        )

        return JsonResponse(
            {
                "success": True,
                "message": f'Товар "{product.title}" добавлен в корзину',
                "basket_count": len(basket),
                "total_cost": str(total_cost),
            }
        )


@method_decorator(require_POST, name="dispatch")
class UpdateBasketItemView(View):
    """Обновление количества товара в сессионной корзине"""

    def post(self, request, item_id):
        basket = SessionBasket(request)
        try:
            count = int(request.POST.get("count", 1))
        except ValueError:
            return JsonResponse(
                {"success": False, "message": "Некорректное количество"}
            )

        if count <= 0:
            basket.remove(item_id, basket.basket.get(str(item_id), {}).get("count", 0))
        else:
            product = get_object_or_404(Product, pk=item_id)
            basket.add(product, count=count, update_count=True)

        product = get_object_or_404(Product, pk=item_id)
        basket.add(product, count=count, update_count=True)

        item = basket.basket[str(item_id)]
        total_price = str(Decimal(item["price"]) * item["count"])

        total_cost = sum(
            Decimal(item["price"]) * item["count"] for item in basket.basket.values()
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Количество обновлено",
                "total_price": total_price,
                "basket_count": len(basket),
                "total_cost": str(total_cost),
            }
        )


@method_decorator(require_POST, name="dispatch")
class RemoveFromBasketView(View):
    """Удаление товара из сессионной корзины"""

    def post(self, request, item_id):
        basket = SessionBasket(request)
        basket.remove(item_id, basket.basket.get(str(item_id), {}).get("count", 0))

        total_cost = sum(
            Decimal(item["price"]) * item["count"] for item in basket.basket.values()
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Товар удалён из корзины",
                "basket_count": len(basket),
                "total_cost": str(total_cost),
            }
        )


class OrderListView(LoginRequiredMixin, ListView):
    """Список заказов пользователя"""

    model = Order
    template_name = "shop/order_list.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "items__product"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Мои заказы"
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о заказе"""

    model = Order
    template_name = "shop/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "items__product"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Заказ #{self.object.id}"
        return context


class CreateOrderView(LoginRequiredMixin, View):
    """Создание заказа из сессионной корзины"""

    def post(self, request):
        basket = SessionBasket(request)

        if len(basket) == 0:
            return JsonResponse({"success": False, "message": "Корзина пуста"})

        # Создаём заказ
        order = Order.objects.create(user=request.user)

        # Добавляем товары из сессии в заказ
        for item in basket:
            product = item["product"]
            OrderItem.objects.create(
                order=order,
                product=product,
                count=item["count"],
                price=product.price,
            )

        # Очищаем сессионную корзину
        basket.clear()

        return JsonResponse(
            {"success": True, "message": "Заказ успешно создан", "order_id": order.id}
        )


class PromotionListView(ListView):
    """Список активных акций"""

    model = Promotion
    template_name = "shop/promotion_list.html"
    context_object_name = "promotions"
    paginate_by = 10

    def get_queryset(self):
        return Promotion.objects.filter(is_active=True).prefetch_related("products")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Акции"
        return context


class PromotionDetailView(DetailView):
    """Детальная информация об акции"""

    model = Promotion
    template_name = "shop/promotion_detail.html"
    context_object_name = "promotion"

    def get_queryset(self):
        return Promotion.objects.prefetch_related("products__images")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.object.title
        return context


class PromotionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Создание новой акции"""

    model = Promotion
    form_class = PromotionForm
    template_name = "shop/promotion_form.html"
    success_url = reverse_lazy("shop:promotion_list")
    success_message = "Акция успешно создана"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Создать акцию"
        return context


class PromotionUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Редактирование акции"""

    model = Promotion
    form_class = PromotionForm
    template_name = "shop/promotion_form.html"
    success_url = reverse_lazy("shop:promotion_list")
    success_message = "Акция успешно обновлена"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Редактировать акцию: {self.object.title}"
        return context


class PromotionDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Удаление акции"""

    model = Promotion
    template_name = "shop/promotion_confirm_delete.html"
    success_url = reverse_lazy("shop:promotion_list")
    success_message = "Акция успешно удалена"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Удалить акцию: {self.object.title}"
        return context


class TagListView(ListView):
    """Список всех тегов"""

    model = Tag
    template_name = "shop/tag_list.html"
    context_object_name = "tags"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Теги"
        return context


class TagDetailView(DetailView):
    """Детальная информация о теге с товарами"""

    model = Tag
    template_name = "shop/tag_detail.html"
    context_object_name = "tag"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = self.get_object()

        # Получаем товары с этим тегом
        products = (
            tag.products.all().select_related("category").prefetch_related("images")
        )
        paginator = Paginator(products, 12)
        page_number = self.request.GET.get("page")
        context["products"] = paginator.get_page(page_number)

        context["title"] = f"Тег: {tag.name}"
        return context


class TagCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Создание нового тега"""

    model = Tag
    form_class = TagForm
    template_name = "shop/tag_form.html"
    success_url = reverse_lazy("shop:tag_list")
    success_message = "Тег успешно создан"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Создать тег"
        return context


class TagUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Редактирование тега"""

    model = Tag
    form_class = TagForm
    template_name = "shop/tag_form.html"
    success_url = reverse_lazy("shop:tag_list")
    success_message = "Тег успешно обновлен"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Редактировать тег: {self.object.name}"
        return context


class TagDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Удаление тега"""

    model = Tag
    template_name = "shop/tag_confirm_delete.html"
    success_url = reverse_lazy("shop:tag_list")
    success_message = "Тег успешно удален"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Удалить тег: {self.object.name}"
        return context


class ImageCategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Создание изображения для категории"""

    model = ImageCategory
    form_class = ImageCategoryForm
    template_name = "shop/image_category_form.html"
    success_url = reverse_lazy("shop:category_list")
    success_message = "Изображение категории успешно создано"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавить изображение категории"
        return context


class ImageCategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Редактирование изображения категории"""

    model = ImageCategory
    form_class = ImageCategoryForm
    template_name = "shop/image_category_form.html"
    success_url = reverse_lazy("shop:category_list")
    success_message = "Изображение категории успешно обновлено"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Редактировать изображение: {self.object.category.title}"
        return context


class ImageCategoryDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Удаление изображения категории"""

    model = ImageCategory
    template_name = "shop/image_category_confirm_delete.html"
    success_url = reverse_lazy("shop:category_list")
    success_message = "Изображение категории успешно удалено"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Удалить изображение: {self.object.category.title}"
        return context


class ImageProductCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Создание изображения для товара"""

    model = ImageProduct
    form_class = ImageProductForm
    template_name = "shop/image_product_form.html"
    success_url = reverse_lazy("shop:product_list")
    success_message = "Изображение товара успешно создано"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавить изображение товара"
        return context


class ImageProductUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Редактирование изображения товара"""

    model = ImageProduct
    form_class = ImageProductForm
    template_name = "shop/image_product_form.html"
    success_url = reverse_lazy("shop:product_list")
    success_message = "Изображение товара успешно обновлено"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Редактировать изображение: {self.object.product.title}"
        return context


class ImageProductDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Удаление изображения товара"""

    model = ImageProduct
    template_name = "shop/image_product_confirm_delete.html"
    success_url = reverse_lazy("shop:product_list")
    success_message = "Изображение товара успешно удалено"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Удалить изображение: {self.object.product.title}"
        return context
