// Shop JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Basket functionality
    initBasketHandlers();

    // Search functionality
    initSearchHandlers();

    // Image preview
    initImagePreview();
});

// Basket handlers
function initBasketHandlers() {
    // Add to basket
    document.querySelectorAll('.add-to-basket').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            addToBasket(productId, this);
        });
    });

    // Update basket item quantity
    document.querySelectorAll('.update-basket-item').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const itemId = this.dataset.itemId;
            const count = this.closest('.quantity-controls').querySelector('.quantity-input').value;
            updateBasketItem(itemId, count, this);
        });
    });

    // Remove from basket
    document.querySelectorAll('.remove-from-basket').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const itemId = this.dataset.itemId;
            removeFromBasket(itemId, this);
        });
    });

    // Create order
    const createOrderBtn = document.querySelector('.create-order');
    if (createOrderBtn) {
        createOrderBtn.addEventListener('click', function(e) {
            e.preventDefault();
            createOrder(this);
        });
    }
}

// Add to basket function
function addToBasket(productId, button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="loading"></span> Добавление...';
    button.disabled = true;

    fetch(`/shop/basket/add/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(data.message, 'success');
            updateBasketCount(data.basket_count);
        } else {
            showMessage(data.message || 'Ошибка при добавлении товара', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('Ошибка при добавлении товара', 'error');
    })
    .finally(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

// Update basket item function
function updateBasketItem(itemId, count) {
    fetch(`/shop/basket/update/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `count=${count}`
    })
    .then(response => response.json())
    .then(data => {
        if(data.success){
            // Обновляем визуально сумму
            const itemElement = document.querySelector(`[data-item-id="${itemId}"]`);
            const totalEl = itemElement.querySelector('.item-total');
            totalEl.textContent = data.total_price + ' руб.';
            document.querySelectorAll('.basket-count').forEach(el => el.textContent = data.basket_count);
        } else {
            alert(data.message || 'Ошибка при обновлении корзины');
        }
    });
}

// Remove from basket function
function removeFromBasket(itemId) {
    if(!confirm('Удалить товар из корзины?')) return;

    fetch(`/shop/basket/remove/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
    .then(response => response.json())
    .then(data => {
        if(data.success){
            const itemElement = document.querySelector(`[data-item-id="${itemId}"]`);
            itemElement.remove();
            document.querySelectorAll('.basket-count').forEach(el => el.textContent = data.basket_count);
        } else {
            alert(data.message || 'Ошибка при удалении товара');
        }
    });
}


// Create order function
function createOrder(button) {
    if (!confirm('Создать заказ из корзины?')) {
        return;
    }

    const originalText = button.innerHTML;
    button.innerHTML = '<span class="loading"></span> Создание заказа...';
    button.disabled = true;

    fetch('/shop/orders/create/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(data.message, 'success');
            setTimeout(() => {
                window.location.href = `/shop/orders/${data.order_id}/`;
            }, 1500);
        } else {
            showMessage(data.message || 'Ошибка при создании заказа', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('Ошибка при создании заказа', 'error');
    })
    .finally(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

// Search handlers
function initSearchHandlers() {
    const searchForm = document.querySelector('#search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            performSearch();
        });
    }

    // Auto-submit on filter change
    document.querySelectorAll('.filter-input').forEach(input => {
        input.addEventListener('change', function() {
            performSearch();
        });
    });
}

// Perform search
function performSearch() {
    const form = document.querySelector('#search-form');
    if (!form) return;

    const formData = new FormData(form);
    const params = new URLSearchParams();

    for (let [key, value] of formData.entries()) {
        if (value) {
            params.append(key, value);
        }
    }

    const url = new URL(window.location);
    url.search = params.toString();
    window.location.href = url.toString();
}

// Image preview handlers
function initImagePreview() {
    document.querySelectorAll('input[type="file"][accept*="image"]').forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    showImagePreview(e.target.result, this);
                };
                reader.readAsDataURL(file);
            }
        });
    });
}

// Show image preview
function showImagePreview(src, input) {
    let preview = input.parentNode.querySelector('.image-preview');
    if (!preview) {
        preview = document.createElement('div');
        preview.className = 'image-preview mt-2';
        input.parentNode.appendChild(preview);
    }

    preview.innerHTML = `
        <img src="${src}" alt="Preview" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">
    `;
}

function getCSRFToken() {
    // 1) Сначала ищем в meta-теге
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) {
        return meta.getAttribute("content");
    }

    // 2) Если meta нет — пробуем из cookie
    return getCookie("csrftoken");
}
// Utility functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showMessage(message, type = 'info') {
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';

    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    // Remove existing alerts
    document.querySelectorAll('.alert').forEach(alert => alert.remove());

    // Add new alert
    const container = document.querySelector('.main-content') || document.body;
    container.insertAdjacentHTML('afterbegin', alertHtml);

    // Auto-hide after 5 seconds
    setTimeout(() => {
        const alert = container.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

function updateBasketCount(count) {
    const basketCount = document.querySelector('.basket-count');
    if (basketCount) {
        basketCount.textContent = count;
    }
}

function updateItemTotal(itemId, totalPrice) {
    const itemElement = document.querySelector(`[data-item-id="${itemId}"]`).closest('.basket-item');
    const totalElement = itemElement.querySelector('.item-total');
    if (totalElement) {
        totalElement.textContent = `${totalPrice} руб.`;
    }
}

function removeBasketItemElement(itemId) {
    const itemElement = document.querySelector(`[data-item-id="${itemId}"]`).closest('.basket-item');
    if (itemElement) {
        itemElement.remove();
    }
}

// Quantity controls
function increaseQuantity(input) {
    input.value = parseInt(input.value) + 1;
    input.dispatchEvent(new Event('change'));
}

function decreaseQuantity(input) {
    if (parseInt(input.value) > 1) {
        input.value = parseInt(input.value) - 1;
        input.dispatchEvent(new Event('change'));
    }
}

// Price formatting
function formatPrice(price) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    }).format(price);
}

// Lazy loading for images
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading when DOM is ready
document.addEventListener('DOMContentLoaded', initLazyLoading);
