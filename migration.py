import os

from models.database import DATABASE_NAME, create_db

from models.user import User
from models.user_info import UserInfo
from models.product import Product
from models.offer import Offer
from models.notification import Notification

if __name__ == '__main__':
    db_is_created = os.path.exists(DATABASE_NAME)
    if not db_is_created:
        create_db()


