from main_models.item import *
from main_models.address import *
from main_models.order import *
from main_models.tag import *
from main_models.user import ShopUser
from main_models.save_card import SaveCard
from main_models.address import Address
from main_models.stock_record import StockRecord
import signals


# Create your models here.

# To prevent code cleanup from removing signals from imports
if signals:
    pass