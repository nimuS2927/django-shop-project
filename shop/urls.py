from django.urls import path

from shop import views
from shop import views_api

app_name = "shop"

urlpatterns = [
    path("", views.StartPageView.as_view(), name="start_page"),
    # ==================== CATEGORY URLS ====================
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path(
        "categories/<int:pk>/",
        views.CategoryDetailView.as_view(),
        name="category_detail",
    ),
    path(
        "categories/create/", views.CategoryCreateView.as_view(), name="category_create"
    ),
    path(
        "categories/<int:pk>/update/",
        views.CategoryUpdateView.as_view(),
        name="category_update",
    ),
    path(
        "categories/<int:pk>/delete/",
        views.CategoryDeleteView.as_view(),
        name="category_delete",
    ),
    # ==================== PRODUCT URLS ====================
    path("products/", views.ProductListView.as_view(), name="product_list"),
    path(
        "products/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"
    ),
    path("products/create/", views.ProductCreateView.as_view(), name="product_create"),
    path(
        "products/<int:pk>/update/",
        views.ProductUpdateView.as_view(),
        name="product_update",
    ),
    path(
        "products/<int:pk>/delete/",
        views.ProductDeleteView.as_view(),
        name="product_delete",
    ),
    # ==================== BASKET URLS ====================
    path("basket/", views.BasketView.as_view(), name="basket"),
    path(
        "basket/add/<int:product_id>/",
        views.AddToBasketView.as_view(),
        name="add_to_basket",
    ),
    path(
        "basket/update/<int:item_id>/",
        views.UpdateBasketItemView.as_view(),
        name="update_basket_item",
    ),
    path(
        "basket/remove/<int:item_id>/",
        views.RemoveFromBasketView.as_view(),
        name="remove_from_basket",
    ),
    # ==================== ORDER URLS ====================
    path("orders/", views.OrderListView.as_view(), name="order_list"),
    path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
    path("orders/create/", views.CreateOrderView.as_view(), name="create_order"),
    # ==================== PROMOTION URLS ====================
    path("promotions/", views.PromotionListView.as_view(), name="promotion_list"),
    path(
        "promotions/<int:pk>/",
        views.PromotionDetailView.as_view(),
        name="promotion_detail",
    ),
    path(
        "promotions/create/",
        views.PromotionCreateView.as_view(),
        name="promotion_create",
    ),
    path(
        "promotions/<int:pk>/update/",
        views.PromotionUpdateView.as_view(),
        name="promotion_update",
    ),
    path(
        "promotions/<int:pk>/delete/",
        views.PromotionDeleteView.as_view(),
        name="promotion_delete",
    ),
    # ==================== TAG URLS ====================
    path("tags/", views.TagListView.as_view(), name="tag_list"),
    path("tags/<int:pk>/", views.TagDetailView.as_view(), name="tag_detail"),
    path("tags/create/", views.TagCreateView.as_view(), name="tag_create"),
    path("tags/<int:pk>/update/", views.TagUpdateView.as_view(), name="tag_update"),
    path("tags/<int:pk>/delete/", views.TagDeleteView.as_view(), name="tag_delete"),
    # ==================== IMAGE URLS ====================
    # Category Images
    path(
        "images/category/create/",
        views.ImageCategoryCreateView.as_view(),
        name="image_category_create",
    ),
    path(
        "images/category/<int:pk>/update/",
        views.ImageCategoryUpdateView.as_view(),
        name="image_category_update",
    ),
    path(
        "images/category/<int:pk>/delete/",
        views.ImageCategoryDeleteView.as_view(),
        name="image_category_delete",
    ),
    # Product Images
    path(
        "images/product/create/",
        views.ImageProductCreateView.as_view(),
        name="image_product_create",
    ),
    path(
        "images/product/<int:pk>/update/",
        views.ImageProductUpdateView.as_view(),
        name="image_product_update",
    ),
    path(
        "images/product/<int:pk>/delete/",
        views.ImageProductDeleteView.as_view(),
        name="image_product_delete",
    ),
]


# API URLS
urlpatterns += [
    path(
        "api/categories/",
        views_api.CategoryApiView.as_view(),
        name="api_categories",
    ),
    path(
        "api/catalog/",
        views_api.CatalogAPIView.as_view(),
        name="api_catalog",
    ),
    path(
        "api/promotions/",
        views_api.PromotionAPIView.as_view(),
        name="api_promotions",
    ),
]
