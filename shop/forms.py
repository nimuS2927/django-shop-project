from django import forms
from django.contrib.auth import get_user_model

from .models import Category
from .models import ImageCategory
from .models import ImageProduct
from .models import Product
from .models import Promotion
from .models import PromotionProduct
from .models import Tag

User = get_user_model()


class CategoryForm(forms.ModelForm):
    """Форма для создания и редактирования категории"""

    class Meta:
        model = Category
        fields = ["title", "parent"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите название категории",
                }
            ),
            "parent": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {"title": "Название категории", "parent": "Родительская категория"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Исключаем текущую категорию из списка возможных родителей
        if self.instance.pk:
            self.fields["parent"].queryset = Category.objects.exclude(
                pk=self.instance.pk
            )
        else:
            self.fields["parent"].queryset = Category.objects.all()


class ProductForm(forms.ModelForm):
    """Форма для создания и редактирования товара"""

    class Meta:
        model = Product
        fields = ["title", "description", "category", "price", "count", "available"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите название товара",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Введите описание товара",
                }
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                }
            ),
            "count": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "placeholder": "0"}
            ),
            "available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "title": "Название товара",
            "description": "Описание",
            "category": "Категория",
            "price": "Цена (руб.)",
            "count": "Количество на складе",
            "available": "Доступно к продаже",
        }


class ProductSearchForm(forms.Form):
    """Форма поиска и фильтрации товаров"""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Поиск по названию или описанию...",
            }
        ),
        label="Поиск",
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Все категории",
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Категория",
    )

    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        empty_label="Все теги",
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Тег",
    )

    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
                "placeholder": "От",
            }
        ),
        label="Цена от",
    )

    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
                "placeholder": "До",
            }
        ),
        label="Цена до",
    )

    available = forms.ChoiceField(
        choices=[("", "Все товары"), ("true", "Доступные"), ("false", "Недоступные")],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Доступность",
    )


class PromotionForm(forms.ModelForm):
    """Форма для создания и редактирования акции"""

    class Meta:
        model = Promotion
        fields = [
            "title",
            "description",
            "discount_percent",
            "start_date",
            "end_date",
            "is_active",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Введите название акции"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Введите описание акции",
                }
            ),
            "discount_percent": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "100",
                    "placeholder": "0",
                }
            ),
            "start_date": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "end_date": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "title": "Название акции",
            "description": "Описание",
            "discount_percent": "Скидка (%)",
            "start_date": "Дата начала",
            "end_date": "Дата окончания",
            "is_active": "Активна",
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date >= end_date:
            value_err = "Дата окончания должна быть позже даты начала"
            raise forms.ValidationError(value_err)

        return cleaned_data


class PromotionProductForm(forms.ModelForm):
    """Форма для добавления товара в акцию"""

    class Meta:
        model = PromotionProduct
        fields = ["product", "limit", "price_with_discount"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-control"}),
            "limit": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": "Без ограничений",
                }
            ),
            "price_with_discount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                }
            ),
        }
        labels = {
            "product": "Товар",
            "limit": "Лимит продаж",
            "price_with_discount": "Цена со скидкой",
        }


class TagForm(forms.ModelForm):
    """Форма для создания и редактирования тега"""

    class Meta:
        model = Tag
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Введите название тега"}
            )
        }
        labels = {"name": "Название тега"}


class ImageCategoryForm(forms.ModelForm):
    """Форма для создания и редактирования изображения категории"""

    class Meta:
        model = ImageCategory
        fields = ["src", "alt", "category"]
        widgets = {
            "src": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "alt": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Описание изображения"}
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "src": "Изображение",
            "alt": "Описание изображения",
            "category": "Категория",
        }


class ImageProductForm(forms.ModelForm):
    """Форма для создания и редактирования изображения товара"""

    class Meta:
        model = ImageProduct
        fields = ["src", "alt", "product"]
        widgets = {
            "src": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "alt": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Описание изображения"}
            ),
            "product": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "src": "Изображение",
            "alt": "Описание изображения",
            "product": "Товар",
        }
