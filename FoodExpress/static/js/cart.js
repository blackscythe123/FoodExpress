// Cart functionality

// Add item to cart
function addToCart(itemId, quantity) {
    fetch('/api/cart/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            item_id: itemId,
            quantity: quantity
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Update cart count in navbar
            updateCartCount(data.cart_count);
            
            // Show success message
            showToast(data.message);
        } else {
            displayErrorMessage(data.message || 'Failed to add item to cart');
        }
    })
    .catch(error => {
        console.error('Error adding to cart:', error);
        displayErrorMessage('Failed to add item to cart. Please try again.');
    });
}

// Update cart item quantity
function updateCartItem(itemId, quantity) {
    fetch('/api/cart/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            item_id: itemId,
            quantity: quantity
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Update cart count in navbar
            updateCartCount(data.cart_count);
            
            // If on cart page, update the display
            if (window.location.pathname === '/cart') {
                updateCartDisplay(data);
            }
        } else {
            displayErrorMessage(data.message || 'Failed to update cart');
        }
    })
    .catch(error => {
        console.error('Error updating cart:', error);
        displayErrorMessage('Failed to update cart. Please try again.');
    });
}

// Remove item from cart
function removeCartItem(itemId) {
    updateCartItem(itemId, 0);
}

// Update cart count in navbar
function updateCartCount(count) {
    const cartCountElement = document.getElementById('cart-count');
    if (cartCountElement) {
        cartCountElement.textContent = count;
        
        // Show or hide based on count
        if (count > 0) {
            cartCountElement.classList.remove('d-none');
        } else {
            cartCountElement.classList.add('d-none');
        }
    }
}

// Update cart display on the cart page
function updateCartDisplay(data) {
    // Reload the page to show updated cart
    // This is a simple approach; for a more sophisticated SPA-like experience,
    // you could update the DOM directly without reloading
    location.reload();
}

// Initialize cart page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Attach event listeners to quantity buttons on cart page
    const quantityInputs = document.querySelectorAll('.cart-quantity-input');
    if (quantityInputs.length > 0) {
        quantityInputs.forEach(input => {
            // Attach to the input change event
            input.addEventListener('change', function() {
                const itemId = this.getAttribute('data-item-id');
                const quantity = parseInt(this.value);
                
                if (quantity <= 0) {
                    // Confirm removal
                    if (confirm('Are you sure you want to remove this item from your cart?')) {
                        removeCartItem(itemId);
                    } else {
                        // Reset to 1 if user cancels removal
                        this.value = 1;
                    }
                } else {
                    // Update quantity
                    updateCartItem(itemId, quantity);
                }
            });
        });
    }
    
    // Attach event listeners to quantity adjustment buttons
    const decrementButtons = document.querySelectorAll('.cart-quantity-decrement');
    const incrementButtons = document.querySelectorAll('.cart-quantity-increment');
    
    decrementButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('.cart-quantity-input');
            const itemId = input.getAttribute('data-item-id');
            const newValue = Math.max(1, parseInt(input.value) - 1);
            
            input.value = newValue;
            updateCartItem(itemId, newValue);
        });
    });
    
    incrementButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('.cart-quantity-input');
            const itemId = input.getAttribute('data-item-id');
            const newValue = Math.min(10, parseInt(input.value) + 1);
            
            input.value = newValue;
            updateCartItem(itemId, newValue);
        });
    });
    
    // Attach event listeners to remove buttons
    const removeButtons = document.querySelectorAll('.cart-item-remove');
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-item-id');
            
            if (confirm('Are you sure you want to remove this item from your cart?')) {
                removeCartItem(itemId);
            }
        });
    });
});
