// Main JavaScript file

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add animation class to elements when they come into view
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    if (animateElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        animateElements.forEach(element => {
            observer.observe(element);
        });
    }

    // Mobile menu toggle
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            const mobileMenu = document.getElementById('mobile-menu');
            if (mobileMenu) {
                mobileMenu.classList.toggle('show');
            }
        });
    }

    // Restaurant filter form
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form values
            const cuisine = document.getElementById('cuisine-filter').value;
            const rating = document.getElementById('rating-filter').value;
            const search = document.getElementById('search-filter').value;
            
            // Build query string
            let queryParams = [];
            if (cuisine) queryParams.push(`cuisine=${encodeURIComponent(cuisine)}`);
            if (rating) queryParams.push(`rating=${encodeURIComponent(rating)}`);
            if (search) queryParams.push(`search=${encodeURIComponent(search)}`);
            
            // Redirect with query parameters
            const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';
            window.location.href = `/restaurants${queryString}`;
        });
    }

    // Clear filters button
    const clearFiltersBtn = document.getElementById('clear-filters');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            window.location.href = '/restaurants';
        });
    }

    // Category filter for restaurant detail page
    const categoryFilter = document.getElementById('category-filter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            const restaurantId = this.getAttribute('data-restaurant-id');
            const selectedCategory = this.value;
            
            fetchMenuItems(restaurantId, selectedCategory);
        });
    }
    
    // Initialize restaurant detail page if needed
    const menuItemsContainer = document.getElementById('menu-items-container');
    if (menuItemsContainer) {
        const restaurantId = menuItemsContainer.getAttribute('data-restaurant-id');
        if (restaurantId) {
            fetchMenuItems(restaurantId, 'all');
        }
    }
});

// Function to fetch menu items by category
function fetchMenuItems(restaurantId, category) {
    const url = `/api/menu_items/${restaurantId}${category !== 'all' ? `?category=${encodeURIComponent(category)}` : ''}`;
    
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            renderMenuItems(data);
        })
        .catch(error => {
            console.error('Error fetching menu items:', error);
            displayErrorMessage('Failed to load menu items. Please try again later.');
        });
}

// Function to render menu items
function renderMenuItems(items) {
    const container = document.getElementById('menu-items-container');
    
    // Clear current content
    container.innerHTML = '';
    
    if (items.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <p class="text-muted">No menu items found in this category.</p>
            </div>
        `;
        return;
    }
    
    // Render each item
    items.forEach(item => {
        const itemCard = document.createElement('div');
        itemCard.className = 'col-md-6 col-lg-4 mb-4';
        
        let dietaryBadges = '';
        if (item.is_vegetarian) {
            dietaryBadges += '<span class="badge bg-success me-1">Vegetarian</span>';
        }
        if (item.is_vegan) {
            dietaryBadges += '<span class="badge bg-success me-1">Vegan</span>';
        }
        if (item.is_gluten_free) {
            dietaryBadges += '<span class="badge bg-warning text-dark">Gluten Free</span>';
        }
        
        itemCard.innerHTML = `
            <div class="card menu-item-card h-100">
                <img src="${item.image_url}" class="card-img-top" alt="${item.name}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <h5 class="card-title">${item.name}</h5>
                        <span class="badge bg-primary">$${item.price.toFixed(2)}</span>
                    </div>
                    <p class="card-text">${item.description}</p>
                    <div class="mb-3">
                        ${dietaryBadges}
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="input-group input-group-sm" style="max-width: 120px;">
                            <button class="btn btn-outline-secondary" type="button" onclick="updateQuantity(this, -1)">-</button>
                            <input type="number" class="form-control text-center item-quantity" value="1" min="1" max="10">
                            <button class="btn btn-outline-secondary" type="button" onclick="updateQuantity(this, 1)">+</button>
                        </div>
                        <button class="btn btn-primary add-to-cart-btn" data-item-id="${item.id}">
                            <i class="fas fa-cart-plus"></i> Add
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(itemCard);
    });
    
    // Add event listeners to the new add-to-cart buttons
    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-item-id');
            const quantityInput = this.closest('.card-body').querySelector('.item-quantity');
            const quantity = parseInt(quantityInput.value);
            
            addToCart(itemId, quantity);
        });
    });
}

// Function to update quantity input
function updateQuantity(button, change) {
    const input = button.parentElement.querySelector('input');
    let value = parseInt(input.value) + change;
    
    // Ensure value is within min/max range
    value = Math.max(1, Math.min(10, value));
    
    input.value = value;
}

// Function to display error messages
function displayErrorMessage(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Find a suitable container for the alert
    const container = document.querySelector('.main-content') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}

// Function to show success toast
function showToast(message) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        // Create toast container if it doesn't exist
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '11';
        document.body.appendChild(container);
    }
    
    const toastId = 'toast-' + Date.now();
    const toastHTML = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <strong class="me-auto">Notification</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    document.getElementById('toast-container').innerHTML += toastHTML;
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 3000 });
    toast.show();
}
