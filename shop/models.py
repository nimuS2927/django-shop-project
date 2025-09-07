from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from mptt.models import MPTTModel
from mptt.models import TreeForeignKey

User = get_user_model()
MAX_DESCRIPTION_LENGTH = 50
ATTR_ERR_MSG = "Модель не имеет необходимых полей count и price"


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        abstract = True


class IDMixin(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, verbose_name="ID")

    class Meta:
        abstract = True


class TotalPriceMixin:
    def total_price(self):
        if hasattr(self, "count") and hasattr(self, "price"):
            return self.count * self.price
        raise AttributeError(ATTR_ERR_MSG)


class Category(IDMixin, TimestampMixin, MPTTModel):
    title = models.CharField(
        max_length=100,
        blank=False,
        verbose_name="Название",
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        blank=True,
        null=True,
        verbose_name="Родительская категория",
    )

    class MPTTMeta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        order_insertion_by = ["title"]

    def __str__(self):
        return f"ID: {self.id} | {self.title}"


def path_to_category_image(instance: "ImageCategory", filename: str) -> str:
    return f"category_{instance.category_id}/images/{filename}"


class ImageCategory(IDMixin, TimestampMixin, models.Model):
    src = models.ImageField(
        null=True,
        blank=True,
        upload_to=path_to_category_image,
        verbose_name="Путь до изображения",
    )
    alt = models.CharField(
        max_length=255,
        blank=True,
        default="Описание для изображения не добавлено",
        verbose_name="Описание изображения",
    )
    category = models.OneToOneField(
        Category,
        on_delete=models.CASCADE,
        related_name="image",
        verbose_name="Категория",
    )

    def __str__(self):
        return str(self.src)


class Product(IDMixin, TimestampMixin, models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Категория",
    )
    price = models.DecimalField(
        blank=True,
        max_digits=8,
        decimal_places=2,
        verbose_name="Цена",
    )
    count = models.PositiveSmallIntegerField(
        blank=True,
        default=1,
    )
    title = models.CharField(
        max_length=100,
        blank=False,
        verbose_name="Название",
    )
    description = models.TextField(blank=True)
    available = models.BooleanField(default=True)
    quantity_sold = models.SmallIntegerField(default=0)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} - {self.price} Руб."

    def get_short_description(self):
        if len(self.description) > MAX_DESCRIPTION_LENGTH:
            return self.description[:MAX_DESCRIPTION_LENGTH] + "..."
        return self.description

    def get_available(self):
        self.available = self.count > 0
        self.save()
        return self.available

    def get_tags_dict(self):
        return list(self.tags.name)

    def get_images(self):
        return [
            {
                "src": image.src.url,
                "alt": image.alt,
            }
            for image in self.images.all()
        ]

    def get_price_with_promotions(self):
        """
        Возвращает цену с учётом активных акций.
        """
        price = self.price
        for promo in self.promotions.all():
            price = promo.apply_price_with_discount(price)
        return price


def path_to_product_image(instance: "ImageProduct", filename: str) -> str:
    return f"product_{instance.product_id}/images/{filename}"


class ImageProduct(IDMixin, TimestampMixin, models.Model):
    src = models.ImageField(
        null=True,
        blank=True,
        upload_to=path_to_product_image,
        verbose_name="Путь до изображения",
    )
    alt = models.CharField(
        max_length=255,
        blank=True,
        default="Описание для изображения не добавлено",
        verbose_name="Описание изображения",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Продукты",
    )

    def __str__(self):
        return str(self.src)


class Tag(IDMixin, TimestampMixin, models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=100)
    products = models.ManyToManyField(Product, related_name="tags")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Promotion(IDMixin, TimestampMixin, models.Model):
    title = models.CharField(verbose_name="Название акции", max_length=255)
    description = models.TextField(verbose_name="Описание", blank=True)
    products = models.ManyToManyField(
        "Product",
        related_name="promotions",
        verbose_name="Товары",
    )
    discount_percent = models.PositiveSmallIntegerField(
        verbose_name="Скидка (%)",
        null=True,
        blank=True,
    )
    start_date = models.DateTimeField(verbose_name="Дата начала")
    end_date = models.DateTimeField(verbose_name="Дата окончания")
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"

    def __str__(self):
        return self.title

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    def apply_price_with_discount(self, price: Decimal) -> Decimal:
        """
        Возвращает цену со скидкой, если акция активна и условия выполнены.
        """
        if not self.is_valid():
            return price
        if self.discount_percent:
            discount = (price * Decimal(self.discount_percent)) / Decimal(100)
            return price - discount
        return price


class Basket(IDMixin, TimestampMixin, models.Model):
    """
    Класс описывающий корзину, используется только для авторизованных пользователей
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=False,
        related_name="basket",
        verbose_name="Корзина",
    )

    class Meta:
        ordering = ["user_id"]
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина {self.user}"


class BasketItem(IDMixin, TimestampMixin, models.Model, TotalPriceMixin):
    basket = models.ForeignKey(
        Basket,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Корзина",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="basket_items",
        verbose_name="Товар",
    )
    count = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("basket", "product")
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"

    def __str__(self):
        return f"{self.product} x {self.count}"


class OrderStatus(models.TextChoices):
    CREATED = "оформлен"
    PAID = "оплачен"
    COMPLETED = "завершен"
    CANCELLED = "отменен"


class Order(IDMixin, TimestampMixin, models.Model):
    user = models.ForeignKey(
        User,
        null=False,
        on_delete=models.CASCADE,
        related_name="Пользователь",
    )
    status = models.CharField(
        max_length=16,
        choices=OrderStatus,
        default=OrderStatus.CREATED,
        verbose_name="Статус заказа",
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Пользователь {self.user} / Заказ ID - {self.id} "

    def total_cost(self):
        return sum([i.total_price for i in self.items])

    def set_status(self, status: OrderStatus) -> None:
        self.status = status
        self.save()

    def mark_paid(self):
        self.set_status(OrderStatus.PAID)

    def mark_completed(self):
        self.set_status(OrderStatus.COMPLETED)

    def mark_cancelled(self):
        self.set_status(OrderStatus.CANCELLED)


class OrderItem(IDMixin, TimestampMixin, models.Model, TotalPriceMixin):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="order_items",
    )
    count = models.PositiveSmallIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("order", "product")
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"

    def __str__(self):
        return f"{self.product} x {self.count}"
