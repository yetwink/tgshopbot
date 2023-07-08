import sqlite3


class DataBase:
    def __init__(self):
        self.database = sqlite3.connect('shop.db', check_same_thread=False)

    # Менеджер для подключения и выполнения запросов в базу
    def manager(self, sql, *args,
                fetchone: bool = False,
                fetchall: bool = False,
                commit: bool = False):
        with self.database as db:
            cursor = db.cursor()
            cursor.execute(sql, args)
            if commit:
                result = db.commit()
            if fetchone:
                result = cursor.fetchone()
            if fetchall:
                result = cursor.fetchall()
            return result


    def create_categories_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS categories(
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name VARCHAR(30) UNIQUE,
            image TEXT
        )
        '''
        self.manager(sql, commit=True)

    def create_products_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS products(
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name VARCHAR(100),
            price DECIMAL(12, 2),
            description VARCHAR(255),
            image TEXT,
            category_id INTEGER REFERENCES categories(category_id)
        )
        '''
        self.manager(sql, commit=True)


    def create_users_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS users(
            user_id BIGINT PRIMARY KEY,
            full_name TEXT,
            phone TEXT
        ) 
        '''
        self.manager(sql, commit=True)
        # INT - INTEGER -2147483648 до 2147483647
        # BIGINT -9223372036854775808 до 9223372036854775808
        # TINYINT -128 до 127
    def get_user_by_id(self, chat_id):
        sql = '''
        SELECT * FROM users WHERE user_id = ?
        '''
        return self.manager(sql, chat_id, fetchone=True)

    def save_user(self, user_id, full_name, phone):
        sql = '''
        INSERT INTO users(user_id, full_name, phone) VALUES (?,?,?)
        '''
        self.manager(sql, user_id, full_name, phone, commit=True)

    def insert_into_categories(self):
        sql = '''
        INSERT INTO categories(category_name, image) VALUES 
        ('Сеты', 'images/set/category.jpg')
        '''
        self.manager(sql, commit=True)

    def insert_into_products(self):
        sql = '''
        INSERT INTO products(product_name, price, description, image, category_id)
        VALUES 
        ('Комбо плюс горячий (Зеленый чай)', 16000, 'Новый сет. Популярный', 'images/set/1.jpg', 1),
        ('ФитCombo', 30000, 'Новый сет. Популярный', 'images/set/2.jpg', 1),
        ('COMBO +', 16000, 'Самое выгодное предложение! Горячий хрустящий картофель фри и стакан Pepsi', 'images/set/3.jpg', 1),
        ('Комбо плюс горячий (Черный чай)', 16000, 'Новый сет. Популярный', 'images/set/4.jpg', 1)
        '''
        self.manager(sql, commit=True)

    def get_categories(self):
        sql = '''
        SELECT category_name FROM categories;
        '''
        return self.manager(sql, fetchall=True)

    def get_category_detail(self, category_name):
        sql = '''
        SELECT category_id, image FROM categories WHERE category_name = ?
        '''
        return self.manager(sql, category_name, fetchone=True)  # ('', '')

    def get_products_names(self, category_id):
        sql = '''
        SELECT product_name FROM products WHERE category_id = ?
        '''
        return self.manager(sql, category_id, fetchall=True)

    def get_all_products_names(self):
        sql = '''
        SELECT product_name FROM products
        '''
        return self.manager(sql, fetchall=True)

    def get_product_detail(self, product_name):
        sql = '''
        SELECT * FROM products WHERE product_name = ?
        '''
        return self.manager(sql, product_name, fetchone=True)

    # fetchone[0] - ('', ) -> ''
    # fetchone - ('', '', '', '')
    # fetchall - [('', ''), ('', ''), ('', ''), ('', ''), ('', '')]

    def get_category_by_id(self, category_id):
        sql = '''
        SELECT * FROM categories WHERE category_id = ?
        '''
        return self.manager(sql, category_id, fetchone=True)


    def create_carts_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS carts(
            cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(user_id) UNIQUE,
            total_price DECIMAL(12, 2) DEFAULT 0,
            total_products INTEGER DEFAULT 0
        )
        '''
        self.manager(sql, commit=True)

    def create_cart_products_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS cart_products(
            cart_product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cart_id INTEGER REFERENCES carts(cart_id),
            product_name VARCHAR(50) NOT NULL,
            quantity INTEGER NOT NULL,
            final_price DECIMAL(12, 2) NOT NULL,
            
            UNIQUE(cart_id, product_name)
        )
        '''
        self.manager(sql, commit=True)


    def create_cart_for_user(self, chat_id):
        sql = '''
        INSERT INTO carts(user_id) VALUES (?)
        '''
        self.manager(sql, chat_id, commit=True)

    def get_cart_id(self, chat_id):
        sql = '''
        SELECT cart_id FROM carts WHERE user_id = ?
        '''
        return self.manager(sql, chat_id, fetchone=True)[0]


    def get_product_name_price(self, product_id):
        sql = '''
        SELECT product_name, price FROM products WHERE product_id = ?
        '''
        return self.manager(sql, product_id, fetchone=True)

    def insert_cart_product(self, cart_id, product_name, quantity, final_price):
        sql = '''
        INSERT INTO cart_products(cart_id, product_name, quantity, final_price)
        VALUES (?,?,?,?)
        '''
        self.manager(sql, cart_id, product_name, quantity, final_price, commit=True)

    def update_cart_product(self, cart_id, product_name, quantity, final_price):
        sql = '''
        UPDATE cart_products
        SET
        quantity = ?,
        final_price = ?
        WHERE product_name = ? AND cart_id = ?
        '''
        self.manager(sql, quantity, final_price, product_name, cart_id, commit=True)

    def update_total_price_quantity(self, cart_id):
        sql = '''
        UPDATE carts
        SET total_price = (
            SELECT SUM(final_price) FROM cart_products WHERE cart_id = ?
        ),
        total_products = (
            SELECT SUM(quantity) FROM cart_products WHERE cart_id = ?
        )
        WHERE cart_id = ?
        '''
        self.manager(sql, cart_id, cart_id, cart_id, commit=True)

    def get_total_price_quantity(self, cart_id):
        sql = '''
        SELECT total_products, total_price FROM carts WHERE cart_id = ?
        '''
        return self.manager(sql, cart_id, fetchone=True)

    def get_cart_products(self, cart_id):
        sql = '''
        SELECT cart_product_id, product_name, quantity, final_price FROM cart_products WHERE cart_id = ?
        '''
        return self.manager(sql, cart_id, fetchall=True)

    def add_quantity_to_cart(self, cart_product_id, quantity):
        sql = '''
        UPDATE cart_products
        SET quantity = ? WHERE cart_product_id = ?
        '''
        self.manager(sql, quantity, cart_product_id, commit=True)

    def delete_cart_product(self, cart_product_id):
        sql = '''
        DELETE FROM cart_products WHERE cart_product_id = ?
        '''
        self.manager(sql, cart_product_id, commit=True)

    def delete_cart_products(self, cart_id):
        sql = '''
        DELETE FROM cart_products WHERE cart_id = ?
        '''
        self.manager(sql, cart_id, commit=True)

    def create_orders_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS orders(
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cart_id INTEGER,
            total_price DECIMAL(12, 2) DEFAULT 0,
            total_products INTEGER DEFAULT 0
        )
        '''
        self.manager(sql, commit=True)

    def create_ordered_products_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS order_products(
            order_product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER REFERENCES orders(cart_id),
            product_name TEXT,
            quantity INTEGER,
            total_price DECIMAL(12, 2) DEFAULT 0
        )
        '''
        self.manager(sql, commit=True)

    def get_orders(self, cart_id):
        sql = '''
        SELECT order_id FROM orders WHERE cart_id = ?
        '''
        return self.manager(sql, cart_id, fetchall=True)

    def get_order_products(self, order_id):
        sql = '''
        SELECT * FROM order_products WHERE order_id = ?
        '''
        return self.manager(sql, order_id, fetchall=True)

    def insert_order(self, cart_id, total_price, total_products):
        sql = '''
        INSERT INTO orders(cart_id, total_price, total_products) VALUES (?,?,?)
        '''
        self.manager(sql, cart_id, total_price, total_products, commit=True)

    def get_order_id(self, cart_id):
        sql = '''
        SELECT order_id FROM orders WHERE cart_id = ? ORDER BY order_id DESC LIMIT 1
        '''
        return self.manager(sql, cart_id, fetchone=True)

    def insert_order_products(self, order_id, product_name, quantity, total_price):
        sql = '''
        INSERT INTO order_products(order_id, product_name, quantity, total_price) 
        VALUES (?,?,?,?)
        '''
        self.manager(sql, order_id, product_name, quantity, total_price, commit=True)

    def cart_refresh(self, cart_id):
        sql = '''
        UPDATE carts 
        SET total_price = 0, total_products = 0
        WHERE cart_id = ?
        '''
        self.manager(sql, cart_id, commit=True)

    def get_all_orders(self, cart_id):
        sql = '''
        SELECT * FROM orders WHERE cart_id = ? ORDER BY order_id DESC LIMIT 5
        '''
        return self.manager(sql, cart_id, fetchall=True)

    def get_all_order_products(self, order_id):
        sql = '''
        SELECT * FROM order_products WHERE order_id = ? 
        '''
        return self.manager(sql, order_id, fetchall=True)

    def get_user_fullname_phone(self, chat_id):
        sql = '''
        SELECT full_name, phone FROM users WHERE user_id = ?
        '''
        return self.manager(sql, chat_id, fetchone=True)

    def update_user_fullname_phone(self, chat_id, full_name, phone):
        sql = '''
        UPDATE users
        SET full_name = ?, phone = ?
        WHERE user_id = ?
        '''
        self.manager(sql, full_name, phone, chat_id, commit=True)


