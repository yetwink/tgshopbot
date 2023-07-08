Telegram shop-bot. This bot created with Aiogram + sqlite3.

Here I have implemented a convenient menu where you can select a category > product > select quantity > add to cart. I also added a test payment function, so after each successful order, it is recorded in the database. So I added a function to the bot that displays the user's latest orders along with the details of each order. 

Registration. It is also a test, the verification code of the user's number does not come via SMS, but in the bot itself. All user data is saved to the database. Also, these user data can be changed using the settings in the main menu.

Cart. By adding a product to the menu, all products are saved in the cart when added, and you can switch between categories by adding products to the cart and do an order at the end. When you go to the cart you can see complete list of products and the number of every product can be reduced / increased or deleted. 

Feedback. Bot users can also leave feedback that is sent to the group ID or admin.
