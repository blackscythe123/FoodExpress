// Search and filtering functionality

document.addEventListener('DOMContentLoaded', function() {
    // Restaurant search form
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const searchInput = document.getElementById('search-input');
            if (searchInput && searchInput.value.trim()) {
                window.location.href = `/restaurants?search=${encodeURIComponent(searchInput.value.trim())}`;
            }
        });
    }
    
    // Restaurant filter functionality
    const cuisineFilter = document.getElementById('cuisine-filter');
    const ratingFilter = document.getElementById('rating-filter');
    
    // Auto-submit on filter change
    if (cuisineFilter) {
        cuisineFilter.addEventListener('change', function() {
            applyFilters();
        });
    }
    
    if (ratingFilter) {
        ratingFilter.addEventListener('change', function() {
            applyFilters();
        });
    }
    
    // Function to apply selected filters
    function applyFilters() {
        const cuisine = cuisineFilter ? cuisineFilter.value : '';
        const rating = ratingFilter ? ratingFilter.value : '';
        const searchParam = new URLSearchParams(window.location.search).get('search') || '';
        
        let queryParams = [];
        if (cuisine) queryParams.push(`cuisine=${encodeURIComponent(cuisine)}`);
        if (rating) queryParams.push(`rating=${encodeURIComponent(rating)}`);
        if (searchParam) queryParams.push(`search=${encodeURIComponent(searchParam)}`);
        
        const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';
        window.location.href = `/restaurants${queryString}`;
    }
    
    // Live search functionality for menu items on restaurant page
    const menuSearchInput = document.getElementById('menu-search');
    if (menuSearchInput) {
        menuSearchInput.addEventListener('input', function() {
            const searchValue = this.value.toLowerCase().trim();
            const menuItems = document.querySelectorAll('.menu-item-card');
            
            menuItems.forEach(item => {
                const itemName = item.querySelector('.card-title').textContent.toLowerCase();
                const itemDescription = item.querySelector('.card-text').textContent.toLowerCase();
                
                if (itemName.includes(searchValue) || itemDescription.includes(searchValue)) {
                    item.closest('.col-md-6').style.display = '';
                } else {
                    item.closest('.col-md-6').style.display = 'none';
                }
            });
            
            // Display message if no results
            const visibleItems = document.querySelectorAll('.menu-item-card:not([style*="display: none"])');
            const noResultsElement = document.getElementById('no-menu-results');
            
            if (visibleItems.length === 0 && searchValue !== '') {
                if (!noResultsElement) {
                    const container = document.getElementById('menu-items-container');
                    const noResults = document.createElement('div');
                    noResults.id = 'no-menu-results';
                    noResults.className = 'col-12 text-center py-3';
                    noResults.innerHTML = `<p class="text-muted">No menu items matching "${searchValue}"</p>`;
                    container.appendChild(noResults);
                }
            } else if (noResultsElement) {
                noResultsElement.remove();
            }
        });
    }
});
