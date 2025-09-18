// ========================
// Helper function to get CSRF token
// ========================
function getCSRFToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute("content") : "";
}

// ========================
// Basket item operations
// ========================

function increaseQuantity(productId) {
    const input = document.querySelector(`.quantity-input[data-item-id='${productId}']`);
    const newCount = parseInt(input.value) + 1;
    updateBasketItem(productId, newCount, input);
}

function decreaseQuantity(productId) {
    const input = document.querySelector(`.quantity-input[data-item-id='${productId}']`);
    const newCount = Math.max(1, parseInt(input.value) - 1);
    updateBasketItem(productId, newCount, input);
}

function removeBasketItem(productId) {
    fetch(`/shop/basket/remove/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const itemRow = document.querySelector(`[data-item-id='${productId}']`);
            if (itemRow) itemRow.remove();
            // Обновляем summary корзины с актуальной суммой
            updateBasketSummary(data.basket_count, data.total_cost);
        } else {
            alert(data.message);
        }
    });
}

function updateBasketItem(productId, count, inputElement) {
    fetch(`/shop/basket/update/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `count=${count}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            inputElement.value = count;

            const itemRow = document.querySelector(`[data-item-id='${productId}']`);
            if (itemRow) itemRow.querySelector('.item-total').textContent = parseFloat(data.total_price).toFixed(2) + ' руб.';

            // Обновляем summary корзины с актуальной суммой
            updateBasketSummary(data.basket_count, data.total_cost);
        } else {
            alert(data.message);
        }
    });
}

// ========================
// Update basket summary totals
// ========================
function updateBasketSummary(basketCount, totalCost) {
    // Обновляем количество товаров
    document.querySelectorAll('.basket-count').forEach(el => el.textContent = basketCount);

    // Обновляем общую сумму
    const totalCostElement = document.querySelector('.fw-bold');
    if (totalCostElement) {
        if (totalCost !== undefined && totalCost !== null) {
            totalCostElement.textContent = parseFloat(totalCost).toFixed(2) + ' руб.';
        } else {
            // fallback: пересчёт из DOM (на случай ошибок)
            let sum = 0;
            document.querySelectorAll('.item-total').forEach(el => {
                const value = parseFloat(el.textContent.replace(' руб.', '').replace(',', '.'));
                sum += isNaN(value) ? 0 : value;
            });
            totalCostElement.textContent = sum.toFixed(2) + ' руб.';
        }
    }
}

// ========================
// Create order
// ========================
function createOrder() {
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
            // Перенаправляем на страницу созданного заказа
            window.location.href = `/shop/orders/${data.order_id}/`;
        } else {
            alert(data.message || 'Ошибка при создании заказа');
        }
    })
    .catch(err => {
        console.error('Ошибка при создании заказа:', err);
        alert('Ошибка при создании заказа');
    });
}

// ========================
// Event listeners for inputs
// ========================
document.addEventListener('DOMContentLoaded', () => {
    // Отслеживаем ручной ввод количества
    document.querySelectorAll('.quantity-input').forEach(input => {
        input.addEventListener('change', () => {
            const productId = input.dataset.itemId;
            const count = parseInt(input.value);
            updateBasketItem(productId, count, input);
        });
    });

    // Кнопки удалить
    document.querySelectorAll('.remove-from-basket').forEach(button => {
        button.addEventListener('click', () => {
            const productId = button.dataset.itemId;
            removeBasketItem(productId);
        });
    });

    // Кнопка "Оформить заказ"
    const createOrderBtn = document.querySelector('.create-order');
    if (createOrderBtn) {
        createOrderBtn.addEventListener('click', (e) => {
            e.preventDefault();
            createOrder();
        });
    }
});
