from app import db
from models import User, Restaurant, MenuItem
from werkzeug.security import generate_password_hash

def init_data():
    """Initialize the database with sample data"""
    # Check if we already have data
    if Restaurant.query.count() > 0:
        return
    
    # Create a customer user
    demo_user = User(
        username="demo",
        email="demo@example.com",
        password_hash=generate_password_hash("password"),
        address="123 Main St, City",
        phone="555-1234",
        role="customer"
    )
    db.session.add(demo_user)
    
    # Create an admin user
    admin_user = User(
        username="admin",
        email="admin@example.com",
        password_hash=generate_password_hash("admin123"),
        address="456 Admin Ave, City",
        phone="555-5678",
        role="admin"
    )
    db.session.add(admin_user)
    
    # Create a restaurant owner user
    owner_user = User(
        username="owner",
        email="owner@example.com",
        password_hash=generate_password_hash("owner123"),
        address="789 Owner Blvd, City",
        phone="555-9012",
        role="owner"
    )
    db.session.add(owner_user)
    db.session.flush()  # To get the user ID
    
    # Create restaurants with their menu items
    restaurants = [
        {
            "name": "Bella Italia",
            "description": "Authentic Italian cuisine with a modern twist. Our pasta is made fresh daily and our pizza is cooked in a traditional wood-fired oven.",
            "address": "456 Italian Ave, Foodville",
            "phone": "555-2345",
            "email": "info@bellaitalia.com",
            "rating": 4.7,
            "image_url": "https://images.unsplash.com/photo-1552611052-60b2c00a2be8",
            "cuisine_type": "Italian",
            "menu_items": [
                {
                    "name": "Margherita Pizza",
                    "description": "Classic pizza with tomato sauce, mozzarella, and fresh basil",
                    "price": 12.99,
                    "image_url": "https://images.unsplash.com/photo-1464454709131-ffd692591ee5",
                    "category": "Pizza",
                    "is_vegetarian": True
                },
                {
                    "name": "Spaghetti Carbonara",
                    "description": "Spaghetti with crispy pancetta, egg, pecorino cheese, and black pepper",
                    "price": 14.50,
                    "image_url": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601",
                    "category": "Pasta",
                    "is_vegetarian": False
                },
                {
                    "name": "Tiramisu",
                    "description": "Classic Italian dessert with layers of coffee-soaked ladyfingers and mascarpone cream",
                    "price": 7.99,
                    "image_url": "https://images.unsplash.com/photo-1485963631004-f2f00b1d6606",
                    "category": "Dessert",
                    "is_vegetarian": True
                }
            ]
        },
        {
            "name": "Spice Garden",
            "description": "Experience the rich flavors of authentic Indian cuisine. Our spices are imported directly from India to ensure the most authentic taste.",
            "address": "789 Spice Lane, Foodville",
            "phone": "555-3456",
            "email": "info@spicegarden.com",
            "rating": 4.5,
            "image_url": "https://images.unsplash.com/photo-1554679665-f5537f187268",
            "cuisine_type": "Indian",
            "menu_items": [
                {
                    "name": "Butter Chicken",
                    "description": "Tender chicken cooked in a rich and creamy tomato sauce",
                    "price": 15.99,
                    "image_url": "https://images.unsplash.com/photo-1452708297302-9580a48c8c77",
                    "category": "Main Course",
                    "is_vegetarian": False
                },
                {
                    "name": "Vegetable Biryani",
                    "description": "Fragrant basmati rice cooked with mixed vegetables and aromatic spices",
                    "price": 13.50,
                    "image_url": "https://images.unsplash.com/photo-1447078806655-40579c2520d6",
                    "category": "Rice Dishes",
                    "is_vegetarian": True,
                    "is_vegan": True
                },
                {
                    "name": "Garlic Naan",
                    "description": "Soft flatbread brushed with garlic butter",
                    "price": 3.99,
                    "image_url": "https://images.unsplash.com/photo-1498837167922-ddd27525d352",
                    "category": "Bread",
                    "is_vegetarian": True
                }
            ]
        },
        {
            "name": "Burger Palace",
            "description": "Home of the juiciest gourmet burgers in town. All our beef is sourced from local farms and ground fresh daily.",
            "address": "101 Burger Blvd, Foodville",
            "phone": "555-4567",
            "email": "info@burgerpalace.com",
            "rating": 4.3,
            "image_url": "https://images.unsplash.com/photo-1552729434-12cd1fb0099a",
            "cuisine_type": "American",
            "menu_items": [
                {
                    "name": "Classic Cheeseburger",
                    "description": "Beef patty with cheddar cheese, lettuce, tomato, and special sauce",
                    "price": 10.99,
                    "image_url": "https://images.unsplash.com/photo-1552611052-60b2c00a2be8",
                    "category": "Burgers",
                    "is_vegetarian": False
                },
                {
                    "name": "Veggie Burger",
                    "description": "Plant-based patty with avocado, sprouts, and chipotle mayo",
                    "price": 11.99,
                    "image_url": "https://images.unsplash.com/photo-1464454709131-ffd692591ee5",
                    "category": "Burgers",
                    "is_vegetarian": True,
                    "is_vegan": True
                },
                {
                    "name": "Sweet Potato Fries",
                    "description": "Crispy sweet potato fries with aioli dipping sauce",
                    "price": 4.99,
                    "image_url": "https://images.unsplash.com/photo-1498837167922-ddd27525d352",
                    "category": "Sides",
                    "is_vegetarian": True,
                    "is_vegan": True
                }
            ]
        },
        {
            "name": "Sushi Wave",
            "description": "Fresh, authentic Japanese sushi prepared by master chefs. We use only the freshest seafood delivered daily.",
            "address": "234 Ocean Ave, Foodville",
            "phone": "555-5678",
            "email": "info@sushiwave.com",
            "rating": 4.8,
            "image_url": "https://images.unsplash.com/photo-1464306208223-e0b4495a5553",
            "cuisine_type": "Japanese",
            "menu_items": [
                {
                    "name": "California Roll",
                    "description": "Crab, avocado, and cucumber roll with tobiko",
                    "price": 7.99,
                    "image_url": "https://images.unsplash.com/photo-1464454709131-ffd692591ee5",
                    "category": "Sushi Rolls",
                    "is_vegetarian": False
                },
                {
                    "name": "Vegetable Tempura",
                    "description": "Assorted vegetables lightly battered and fried",
                    "price": 9.50,
                    "image_url": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601",
                    "category": "Appetizers",
                    "is_vegetarian": True,
                    "is_vegan": True
                },
                {
                    "name": "Salmon Nigiri",
                    "description": "Fresh salmon slices over seasoned rice",
                    "price": 5.99,
                    "image_url": "https://images.unsplash.com/34/rcaNUh3pQ9GD8w7Iy8qE__DSC0940.jpg",
                    "category": "Nigiri",
                    "is_vegetarian": False
                }
            ]
        },
        {
            "name": "Mediterranean Delight",
            "description": "Savor the flavors of the Mediterranean with our authentic dishes. From kebabs to falafel, we offer a taste of the Mediterranean coast.",
            "address": "567 Olive St, Foodville",
            "phone": "555-6789",
            "email": "info@meddelight.com",
            "rating": 4.6,
            "image_url": "https://images.unsplash.com/photo-1457460866886-40ef8d4b42a0",
            "cuisine_type": "Mediterranean",
            "menu_items": [
                {
                    "name": "Chicken Shawarma Plate",
                    "description": "Marinated chicken with rice, salad, and garlic sauce",
                    "price": 13.99,
                    "image_url": "https://images.unsplash.com/photo-1464454709131-ffd692591ee5",
                    "category": "Main Course",
                    "is_vegetarian": False
                },
                {
                    "name": "Falafel Wrap",
                    "description": "Crispy falafel with tahini sauce, vegetables, and pickles in a wrap",
                    "price": 9.99,
                    "image_url": "https://images.unsplash.com/photo-1485963631004-f2f00b1d6606",
                    "category": "Wraps",
                    "is_vegetarian": True,
                    "is_vegan": True
                },
                {
                    "name": "Greek Salad",
                    "description": "Tomatoes, cucumbers, olives, feta cheese, and olive oil dressing",
                    "price": 8.50,
                    "image_url": "https://images.unsplash.com/photo-1454944338482-a69bb95894af",
                    "category": "Salads",
                    "is_vegetarian": True
                }
            ]
        },
        {
            "name": "Thai Spice",
            "description": "Authentic Thai cuisine with the perfect balance of sweet, sour, spicy, and savory flavors. Our chefs have trained in Thailand to bring you the most authentic experience.",
            "address": "890 Lemongrass Lane, Foodville",
            "phone": "555-7890",
            "email": "info@thaispice.com",
            "rating": 4.4,
            "image_url": "https://images.unsplash.com/photo-1504674900247-0877df9cc836",
            "cuisine_type": "Thai",
            "menu_items": [
                {
                    "name": "Pad Thai",
                    "description": "Stir-fried rice noodles with egg, tofu, bean sprouts, and peanuts",
                    "price": 12.50,
                    "image_url": "https://images.unsplash.com/photo-1498837167922-ddd27525d352",
                    "category": "Noodles",
                    "is_vegetarian": True
                },
                {
                    "name": "Green Curry",
                    "description": "Chicken in a spicy green curry sauce with bamboo shoots and Thai basil",
                    "price": 13.99,
                    "image_url": "https://images.unsplash.com/photo-1447078806655-40579c2520d6",
                    "category": "Curry",
                    "is_vegetarian": False
                },
                {
                    "name": "Mango Sticky Rice",
                    "description": "Sweet coconut sticky rice with fresh mango slices",
                    "price": 6.99,
                    "image_url": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601",
                    "category": "Dessert",
                    "is_vegetarian": True,
                    "is_vegan": True
                }
            ]
        }
    ]
    
    # Assign the first restaurant to the owner
    for i, restaurant_data in enumerate(restaurants):
        menu_items = restaurant_data.pop('menu_items')
        restaurant = Restaurant(**restaurant_data)
        
        # Assign the first restaurant to our owner
        if i == 0:
            restaurant.owner_id = owner_user.id
            
        db.session.add(restaurant)
        db.session.flush()  # To get the restaurant ID
        
        for item_data in menu_items:
            item_data['restaurant_id'] = restaurant.id
            menu_item = MenuItem(**item_data)
            db.session.add(menu_item)
    
    db.session.commit()
