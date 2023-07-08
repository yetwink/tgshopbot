from data.loader import db

db.create_categories_table()
db.create_products_table()
db.create_users_table()

db.create_carts_table()
db.create_cart_products_table()

db.create_orders_table()
db.create_ordered_products_table()



