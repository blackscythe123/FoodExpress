from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
from models import User, Restaurant, MenuItem, Order, OrderItem, RestaurantAnalytics, MenuItemAnalytics, SystemAnalytics
from utils import get_cart_items, get_cart_total
import json
from datetime import datetime, timedelta

@app.route('/')
def index():
    """Home page with featured restaurants and special offers"""
    featured_restaurants = Restaurant.query.order_by(Restaurant.rating.desc()).limit(4).all()
    return render_template('index.html', featured_restaurants=featured_restaurants)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            # Set session permanent to improve session longevity
            session.permanent = True
            
            # Initialize cart if needed
            if 'cart' not in session:
                session['cart'] = {}
                
            # Force session to be saved
            session.modified = True
            
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            
            # Redirect based on user role
            if next_page:
                return redirect(next_page)
            elif user.is_admin():
                return redirect(url_for('admin_dashboard'))
            elif user.is_owner():
                return redirect(url_for('owner_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'customer')  # Default to customer if not provided
        
        # Validate role - allow customer, owner, or admin for self-registration
        if role not in ['customer', 'owner', 'admin']:
            role = 'customer'
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('register.html')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already taken. Please choose another.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email address already registered. Please use another.', 'danger')
            return render_template('register.html')
        
        # Create new user with specified role
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Automatically log in the user after registration
        login_user(user)
        
        # Set session permanent to improve session longevity
        session.permanent = True
        
        # Initialize cart if needed
        if 'cart' not in session:
            session['cart'] = {}
            
        # Force session to be saved
        session.modified = True
        
        flash(f'Registration successful! You are now logged in as a {role.capitalize()}.', 'success')
        
        # Redirect based on role
        if role == 'owner':
            return redirect(url_for('owner_dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    # Clear user session data
    session.pop('cart', None)
    session.modified = True
    
    # Logout the user
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('profile.html', orders=orders)

@app.route('/profile/edit', methods=['POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    current_user.address = request.form.get('address')
    current_user.phone = request.form.get('phone')
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/restaurants')
def restaurants():
    """List all restaurants"""
    # Get filter parameters
    cuisine = request.args.get('cuisine')
    rating = request.args.get('rating')
    search = request.args.get('search')
    
    # Base query
    query = Restaurant.query
    
    # Apply filters
    if cuisine:
        query = query.filter_by(cuisine_type=cuisine)
    if rating:
        query = query.filter(Restaurant.rating >= float(rating))
    if search:
        query = query.filter(Restaurant.name.ilike(f'%{search}%'))
    
    # Get all cuisine types for filter dropdown
    cuisine_types = db.session.query(Restaurant.cuisine_type).distinct().all()
    cuisine_types = [c[0] for c in cuisine_types]
    
    # Execute query
    restaurants = query.order_by(Restaurant.rating.desc()).all()
    
    return render_template('restaurants.html', 
                          restaurants=restaurants, 
                          cuisine_types=cuisine_types,
                          selected_cuisine=cuisine,
                          selected_rating=rating,
                          search_query=search)

@app.route('/restaurant/<int:restaurant_id>')
def restaurant_detail(restaurant_id):
    """Restaurant detail page with menu items"""
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    categories = db.session.query(MenuItem.category).filter_by(restaurant_id=restaurant_id).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template('restaurant_detail.html', restaurant=restaurant, categories=categories)

@app.route('/api/menu_items/<int:restaurant_id>')
def api_menu_items(restaurant_id):
    """API endpoint for menu items"""
    category = request.args.get('category')
    
    query = MenuItem.query.filter_by(restaurant_id=restaurant_id)
    if category and category != 'all':
        query = query.filter_by(category=category)
    
    menu_items = query.all()
    
    result = []
    for item in menu_items:
        result.append({
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'price': item.price,
            'image_url': item.image_url,
            'category': item.category,
            'is_vegetarian': item.is_vegetarian,
            'is_vegan': item.is_vegan,
            'is_gluten_free': item.is_gluten_free
        })
    
    return jsonify(result)

@app.route('/cart')
def cart():
    """Shopping cart page"""
    cart_items = get_cart_items()
    cart_total = get_cart_total()
    return render_template('cart.html', cart_items=cart_items, cart_total=cart_total)

@app.route('/api/cart/add', methods=['POST'])
def api_add_to_cart():
    """API endpoint to add item to cart"""
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)
    
    # Initialize cart if it doesn't exist
    if 'cart' not in session:
        session['cart'] = {}
    
    # Convert to string because JSON keys must be strings
    item_id_str = str(item_id)
    
    # Add or update quantity in cart
    if item_id_str in session['cart']:
        session['cart'][item_id_str] += quantity
    else:
        session['cart'][item_id_str] = quantity
    
    # Save session
    session.modified = True
    
    # Get updated cart details
    cart_items = get_cart_items()
    cart_total = get_cart_total()
    
    return jsonify({
        'success': True,
        'message': 'Item added to cart!',
        'cart_count': sum(session['cart'].values()),
        'cart_total': cart_total
    })

@app.route('/api/cart/update', methods=['POST'])
def api_update_cart():
    """API endpoint to update cart quantity"""
    data = request.get_json()
    item_id = str(data.get('item_id'))
    quantity = data.get('quantity', 0)
    
    if 'cart' not in session:
        return jsonify({
            'success': False,
            'message': 'Cart is empty'
        })
    
    if item_id in session['cart']:
        if quantity <= 0:
            # Remove item if quantity is 0 or negative
            session['cart'].pop(item_id)
        else:
            # Update quantity
            session['cart'][item_id] = quantity
        
        session.modified = True
        
        cart_items = get_cart_items()
        cart_total = get_cart_total()
        
        return jsonify({
            'success': True,
            'message': 'Cart updated',
            'cart_count': sum(session['cart'].values()),
            'cart_total': cart_total
        })
    
    return jsonify({
        'success': False,
        'message': 'Item not found in cart'
    })

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page and order placement"""
    if request.method == 'POST':
        # Get cart items
        cart_items = get_cart_items()
        
        if not cart_items:
            flash('Your cart is empty!', 'warning')
            return redirect(url_for('cart'))
        
        # Create order
        delivery_address = request.form.get('address')
        delivery_notes = request.form.get('notes')
        
        # Calculate total
        total_amount = get_cart_total()
        
        order = Order(
            user_id=current_user.id,
            status='confirmed',
            delivery_address=delivery_address,
            delivery_notes=delivery_notes,
            total_amount=total_amount
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID without committing
        
        # Add order items
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item['id'],
                quantity=item['quantity'],
                price=item['price']
            )
            db.session.add(order_item)
        
        # Commit the transaction
        db.session.commit()
        
        # Clear the cart
        session.pop('cart', None)
        
        flash('Order placed successfully!', 'success')
        return redirect(url_for('order_confirmation', order_id=order.id))
    
    # GET request - show checkout form
    cart_items = get_cart_items()
    cart_total = get_cart_total()
    
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('cart'))
    
    return render_template('checkout.html', cart_items=cart_items, cart_total=cart_total)

@app.route('/order_confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    """Order confirmation page"""
    order = Order.query.get_or_404(order_id)
    
    # Ensure the order belongs to the current user
    if order.user_id != current_user.id:
        flash('You do not have permission to view this order.', 'danger')
        return redirect(url_for('profile'))
    
    # Get order items with details
    order_items = []
    for item in order.items:
        menu_item = MenuItem.query.get(item.menu_item_id)
        order_items.append({
            'name': menu_item.name,
            'quantity': item.quantity,
            'price': item.price,
            'subtotal': item.price * item.quantity
        })
    
    return render_template('order_confirmation.html', order=order, order_items=order_items)

@app.route('/owner/dashboard')
@login_required
def owner_dashboard():
    """Restaurant owner dashboard page"""
    if not current_user.is_owner():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    # Get the owner's restaurants
    restaurants = Restaurant.query.filter_by(owner_id=current_user.id).all()
    
    # Get analytics for the owner's restaurants
    restaurant_stats = []
    for restaurant in restaurants:
        # Get monthly analytics for the past 6 months
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        analytics = RestaurantAnalytics.query.filter(
            RestaurantAnalytics.restaurant_id == restaurant.id,
            RestaurantAnalytics.date >= six_months_ago
        ).order_by(RestaurantAnalytics.date).all()
        
        # Get total orders and revenue
        total_orders = sum(a.total_orders for a in analytics) if analytics else 0
        total_revenue = sum(a.total_revenue for a in analytics) if analytics else 0
        
        restaurant_stats.append({
            'restaurant': restaurant,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'analytics': analytics
        })
        
    return render_template('owner_dashboard.html', restaurant_stats=restaurant_stats)

@app.route('/owner/restaurant/add', methods=['GET', 'POST'])
@login_required
def add_restaurant():
    """Add a new restaurant"""
    if not current_user.is_owner():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        cuisine_type = request.form.get('cuisine_type')
        address = request.form.get('address')
        phone = request.form.get('phone')
        email = request.form.get('email', '')
        image_url = request.form.get('image_url', '')
        
        # Simple validation
        if not name or not description or not cuisine_type or not address or not phone:
            flash('Please fill in all required fields.', 'danger')
            return render_template('add_restaurant.html')
        
        # Create new restaurant
        restaurant = Restaurant(
            name=name,
            description=description,
            cuisine_type=cuisine_type,
            address=address,
            phone=phone,
            email=email,
            image_url=image_url,
            rating=0.0,  # Initial rating
            owner_id=current_user.id
        )
        
        db.session.add(restaurant)
        db.session.commit()
        
        flash('Restaurant added successfully!', 'success')
        return redirect(url_for('owner_dashboard'))
    
    return render_template('add_restaurant.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard page"""
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    # Get all restaurants
    restaurants = Restaurant.query.all()
    
    # Get all users
    users = User.query.all()
    
    # Get overall system analytics
    system_stats = SystemAnalytics.query.order_by(SystemAnalytics.date.desc()).limit(30).all()
    
    # Calculate totals
    total_users = len(users)
    total_restaurants = len(restaurants)
    total_orders = sum(stat.total_orders for stat in system_stats) if system_stats else 0
    total_revenue = sum(stat.total_revenue for stat in system_stats) if system_stats else 0
    
    return render_template('admin_dashboard.html', 
                          total_users=total_users,
                          total_restaurants=total_restaurants,
                          total_orders=total_orders,
                          total_revenue=total_revenue,
                          system_stats=system_stats,
                          restaurants=restaurants,
                          users=users)

@app.context_processor
def cart_processor():
    """Make cart data available to all templates"""
    if 'cart' in session:
        cart_count = sum(session['cart'].values())
    else:
        cart_count = 0
    
    return {'cart_count': cart_count}

@app.route('/owner/restaurant/edit/<int:restaurant_id>', methods=['GET', 'POST'])
@login_required
def edit_restaurant(restaurant_id):
    """Edit restaurant details"""
    if not current_user.is_owner():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    # Ensure the owner is editing their own restaurant
    if restaurant.owner_id != current_user.id:
        flash('You do not have permission to edit this restaurant.', 'danger')
        return redirect(url_for('owner_dashboard'))
    
    if request.method == 'POST':
        restaurant.name = request.form.get('name')
        restaurant.description = request.form.get('description')
        restaurant.cuisine_type = request.form.get('cuisine_type')
        restaurant.address = request.form.get('address')
        restaurant.phone = request.form.get('phone')
        restaurant.email = request.form.get('email', '')
        restaurant.image_url = request.form.get('image_url', '')
        
        # Simple validation
        if not restaurant.name or not restaurant.description or not restaurant.cuisine_type:
            flash('Please fill in all required fields.', 'danger')
            return render_template('edit_restaurant.html', restaurant=restaurant)
        
        db.session.commit()
        
        flash('Restaurant updated successfully!', 'success')
        return redirect(url_for('owner_dashboard'))
    
    return render_template('edit_restaurant.html', restaurant=restaurant)

@app.route('/owner/restaurant/delete/<int:restaurant_id>', methods=['POST'])
@login_required
def delete_restaurant(restaurant_id):
    """Delete a restaurant"""
    if not current_user.is_owner():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    # Ensure the owner is deleting their own restaurant
    if restaurant.owner_id != current_user.id:
        flash('You do not have permission to delete this restaurant.', 'danger')
        return redirect(url_for('owner_dashboard'))
    
    # Delete associated menu items first
    MenuItem.query.filter_by(restaurant_id=restaurant_id).delete()
    
    # Delete the restaurant
    db.session.delete(restaurant)
    db.session.commit()
    
    flash('Restaurant deleted successfully!', 'success')
    return redirect(url_for('owner_dashboard'))

@app.route('/owner/restaurant/<int:restaurant_id>/menu', methods=['GET'])
@login_required
def manage_menu(restaurant_id):
    """Manage restaurant menu"""
    if not current_user.is_owner():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    # Ensure the owner is managing their own restaurant
    if restaurant.owner_id != current_user.id:
        flash('You do not have permission to manage this restaurant menu.', 'danger')
        return redirect(url_for('owner_dashboard'))
    
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
    categories = db.session.query(MenuItem.category).filter_by(restaurant_id=restaurant_id).distinct().all()
    categories = [c[0] for c in categories] if categories else []
    
    return render_template('manage_menu.html', restaurant=restaurant, menu_items=menu_items, categories=categories)

@app.route('/owner/menu_item/add/<int:restaurant_id>', methods=['GET', 'POST'])
@login_required
def add_menu_item(restaurant_id):
    """Add a new menu item"""
    if not current_user.is_owner():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    # Ensure the owner is adding a menu item to their own restaurant
    if restaurant.owner_id != current_user.id:
        flash('You do not have permission to add items to this restaurant.', 'danger')
        return redirect(url_for('owner_dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        category = request.form.get('category')
        image_url = request.form.get('image_url', '')
        is_vegetarian = 'is_vegetarian' in request.form
        is_vegan = 'is_vegan' in request.form
        is_gluten_free = 'is_gluten_free' in request.form
        
        # Simple validation
        if not name or not price or not category:
            flash('Please fill in all required fields.', 'danger')
            return render_template('add_menu_item.html', restaurant=restaurant)
        
        try:
            price = float(price)
        except ValueError:
            flash('Price must be a valid number.', 'danger')
            return render_template('add_menu_item.html', restaurant=restaurant)
        
        # Create new menu item
        menu_item = MenuItem(
            name=name,
            description=description,
            price=price,
            category=category,
            image_url=image_url,
            is_vegetarian=is_vegetarian,
            is_vegan=is_vegan,
            is_gluten_free=is_gluten_free,
            restaurant_id=restaurant.id
        )
        
        db.session.add(menu_item)
        db.session.commit()
        
        flash('Menu item added successfully!', 'success')
        return redirect(url_for('manage_menu', restaurant_id=restaurant.id))
    
    return render_template('add_menu_item.html', restaurant=restaurant)

@app.route('/owner/menu_item/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_menu_item(item_id):
    """Edit a menu item"""
    if not current_user.is_owner():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    menu_item = MenuItem.query.get_or_404(item_id)
    restaurant = Restaurant.query.get_or_404(menu_item.restaurant_id)
    
    # Ensure the owner is editing a menu item for their own restaurant
    if restaurant.owner_id != current_user.id:
        flash('You do not have permission to edit this menu item.', 'danger')
        return redirect(url_for('owner_dashboard'))
    
    if request.method == 'POST':
        menu_item.name = request.form.get('name')
        menu_item.description = request.form.get('description')
        price = request.form.get('price')
        menu_item.category = request.form.get('category')
        menu_item.image_url = request.form.get('image_url', '')
        menu_item.is_vegetarian = 'is_vegetarian' in request.form
        menu_item.is_vegan = 'is_vegan' in request.form
        menu_item.is_gluten_free = 'is_gluten_free' in request.form
        
        # Simple validation
        if not menu_item.name or not price or not menu_item.category:
            flash('Please fill in all required fields.', 'danger')
            return render_template('edit_menu_item.html', menu_item=menu_item, restaurant=restaurant)
        
        try:
            menu_item.price = float(price)
        except ValueError:
            flash('Price must be a valid number.', 'danger')
            return render_template('edit_menu_item.html', menu_item=menu_item, restaurant=restaurant)
        
        db.session.commit()
        
        flash('Menu item updated successfully!', 'success')
        return redirect(url_for('manage_menu', restaurant_id=restaurant.id))
    
    return render_template('edit_menu_item.html', menu_item=menu_item, restaurant=restaurant)

@app.route('/owner/menu_item/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_menu_item(item_id):
    """Delete a menu item"""
    if not current_user.is_owner():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    menu_item = MenuItem.query.get_or_404(item_id)
    restaurant = Restaurant.query.get_or_404(menu_item.restaurant_id)
    
    # Ensure the owner is deleting a menu item from their own restaurant
    if restaurant.owner_id != current_user.id:
        flash('You do not have permission to delete this menu item.', 'danger')
        return redirect(url_for('owner_dashboard'))
    
    # Delete the menu item
    db.session.delete(menu_item)
    db.session.commit()
    
    flash('Menu item deleted successfully!', 'success')
    return redirect(url_for('manage_menu', restaurant_id=restaurant.id))

# Admin routes for managing users and restaurants
@app.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    """Admin edit user"""
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.role = request.form.get('role')
        user.address = request.form.get('address', '')
        user.phone = request.form.get('phone', '')
        
        # Simple validation
        if not user.username or not user.email or not user.role:
            flash('Please fill in all required fields.', 'danger')
            return render_template('admin_edit_user.html', user=user)
        
        # Check if the new username or email already exists (excluding the current user)
        if User.query.filter(User.username == user.username, User.id != user.id).first():
            flash('Username already taken.', 'danger')
            return render_template('admin_edit_user.html', user=user)
        
        if User.query.filter(User.email == user.email, User.id != user.id).first():
            flash('Email already registered.', 'danger')
            return render_template('admin_edit_user.html', user=user)
        
        db.session.commit()
        
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_edit_user.html', user=user)

@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    """Admin delete user"""
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting self
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    # Delete user's restaurants and their menu items
    for restaurant in user.restaurants:
        MenuItem.query.filter_by(restaurant_id=restaurant.id).delete()
        db.session.delete(restaurant)
    
    # Delete user's orders and their items
    for order in user.orders:
        OrderItem.query.filter_by(order_id=order.id).delete()
        db.session.delete(order)
    
    # Delete the user
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/restaurant/edit/<int:restaurant_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_restaurant(restaurant_id):
    """Admin edit restaurant"""
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    owners = User.query.filter_by(role='owner').all()
    
    if request.method == 'POST':
        restaurant.name = request.form.get('name')
        restaurant.description = request.form.get('description')
        restaurant.cuisine_type = request.form.get('cuisine_type')
        restaurant.address = request.form.get('address')
        restaurant.phone = request.form.get('phone')
        restaurant.email = request.form.get('email', '')
        restaurant.image_url = request.form.get('image_url', '')
        owner_id = request.form.get('owner_id')
        
        # Simple validation
        if not restaurant.name or not restaurant.description or not restaurant.cuisine_type:
            flash('Please fill in all required fields.', 'danger')
            return render_template('admin_edit_restaurant.html', restaurant=restaurant, owners=owners)
        
        if owner_id:
            restaurant.owner_id = owner_id
        
        db.session.commit()
        
        flash('Restaurant updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_edit_restaurant.html', restaurant=restaurant, owners=owners)

@app.route('/admin/restaurant/delete/<int:restaurant_id>', methods=['POST'])
@login_required
def admin_delete_restaurant(restaurant_id):
    """Admin delete restaurant"""
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    # Delete associated menu items first
    MenuItem.query.filter_by(restaurant_id=restaurant_id).delete()
    
    # Delete the restaurant
    db.session.delete(restaurant)
    db.session.commit()
    
    flash('Restaurant deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))
