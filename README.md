![ERD Diagram](docs/customi_ERD.png)
# Customi
Multi-Vendor E-Commerce Platform (Backend focused)
A seller-customer platform
Supports a user with the customer | seller role who can add their own store (1:1) and manages their productstores.
The seller is also considered a customer.
Developed backend using Python/DRF. Implemented REST APIs to connect frontend (React.js)
Data is stored/managed based on the PostgreSQL system


## System Features
- "Best Sellers", "Newest Products", and Categories have been aggregated into an endpoint to associated with the home page.
- Browse products, categories, and stores
- Search for products and stores by name
- View product details including name, images, description, price, discount, rating, and reviews
- Pagination and sorting options (e.g., best selling, highest rated, newest, highest/lowest price)

### User Features (Authenticated)
- OTP-based registration and verification via phone
- JWT authentication for secure login/logout
- Manage profile and addresses (add, update, delete)
- Add/remove products to/from cart
- Checkout process with address selection and order confirmation
- View order history and track status (Pending, Paid, Shipped, Delivered, Cancelled)
- Submit product reviews and ratings (once per product after purchase)

### Seller Features
- Register as a seller and create/manage store profile
- Add, edit (price, discount, description, stock), and delete products
- View and manage store-specific orders and items
