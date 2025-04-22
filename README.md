# FoodFlowWebsite

FoodFlowWebsite is a web application designed to streamline food ordering and management. It provides users with an intuitive interface to browse menus, place orders, and manage their profiles.

## Features

- User registration and login (Customer, Admin)
- Role-based dashboards and navigation
- Menu browsing and item details
- Cart and order management
- Admin dashboard for managing menu items and orders
- Responsive UI

## Project Structure

```
FoodFlowWebsite/
├── src/
│   ├── components/
│   ├── pages/
│   ├── App.js
│   ├── index.js
├── public/
│   ├── index.html
├── backend/
│   ├── server.js
│   ├── models/
│   ├── routes/
├── package.json
├── README.md
```

## Technologies Used

- **Frontend:** React
- **Backend:** Node.js, Express
- **Database:** MongoDB
- **Styling:** CSS/SCSS/Styled Components

## Setup & Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/FoodFlowWebsite.git
    cd FoodFlowWebsite
    ```

2. **Install dependencies:**
    ```bash
    npm install
    ```
    For backend dependencies (if separate):
    ```bash
    cd backend
    npm install
    cd ..
    ```

3. **Set up environment variables:**
    - `MONGODB_URI`: MongoDB connection string
    - `JWT_SECRET`: Secret key for authentication

4. **Run the application:**
    - Start the backend:
      ```bash
      npm run server
      ```
    - Start the frontend:
      ```bash
      npm start
      ```

5. **Access the app:**
    - Open [http://localhost:3000](http://localhost:3000) in your browser.

## User Roles

- **Customer:** Can browse menu, add to cart, and place orders.
- **Admin:** Can manage menu items, view and manage orders.

## Development Notes

- Database collections are created automatically on first run.
- The UI uses React and modern CSS frameworks.
- API endpoints are provided for menu, cart, and order management.

## License

MIT License

---

**FoodFlowWebsite** &copy; 2024-present
