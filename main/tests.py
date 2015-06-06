import decimal
import datetime

from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy
from main.main_models.item import Item

from main.main_models.order import Status, Order


class OrderTestCase(TestCase):
    def setUp(self):
        self.orders = mommy.make('main.Order', _quantity=20, make_m2m=True)
        self.old_order = mommy.make('main.Order', make_m2m=True)
        self.old_order.date_placed = timezone.now() - datetime.timedelta(days=45)
        self.single_order = mommy.make('main.Order', make_m2m=True)

    def test_to_unicode(self):
        self.assertEqual(str(self.single_order), str(self.single_order.id))

    def test_weight_set_automatically(self):
        for order in self.orders:
            self.assertEqual(type(order.weight), decimal.Decimal)
            self.assertNotEqual(order.weight, None)
            self.assertNotEqual(order.weight, 0.00)

            total_weight = decimal.Decimal()
            items = Order.objects.get(id=order.id).items.all()
            for item in items:
                total_weight += item.weight

            self.assertEqual(total_weight, order.weight)

    def test_total_price_set_automatically(self):
        for order in self.orders:
            self.assertEqual(type(order._total_price), decimal.Decimal)
            self.assertNotEqual(order.total_price, None)
            self.assertNotEqual(order.total_price, 0.00)

            total_price = decimal.Decimal()
            items = Order.objects.get(id=order.id).items.all()
            for item in items:
                total_price += item.price

            self.assertEqual(total_price, order.total_price)

    def test_recently_placed(self):
        for order in self.orders:
            self.assertEqual(order.recently_placed(), True)

    def test_recently_placed_with_old_order(self):
        self.assertEqual(self.old_order.recently_placed(), False)

    def test_setters_throw_exception(self):
        with self.assertRaises(AttributeError):
            self.old_order.total_price = decimal.Decimal(5.00)

        with self.assertRaises(AttributeError):
            self.old_order.last_modified = timezone.now()

        with self.assertRaises(AttributeError):
            self.old_order.weight = decimal.Decimal(1.25)

    def test_current_status_property(self):
        self.assertIsInstance(self.single_order.current_status, Status)

    def test_current_status_property_setter(self):
        old_last_modified = self.single_order.last_modified
        status = Status.objects.get(pk=1)
        self.single_order.current_status = status
        self.assertNotEqual(self.single_order.last_modified, old_last_modified)
        self.assertEqual(self.single_order.current_status, status)

class ItemTestCase(TestCase):
    def setUp(self):
        self.items = mommy.make('main.Item', make_m2m=True, _quantity=25)
        self.single_item_no_sales = mommy.make('main.Item', make_m2m=True)
        self.single_item_sold = mommy.make('main.Item', make_m2m=True)
        self.single_item_sold_multiple_times = mommy.make('main.Item', make_m2m=True)
        self.single_item_sold_old_orders = mommy.make('main.item', make_m2m=True)
        self.order_with_sold_item = mommy.make('main.Order', items=[self.single_item_sold], make_m2m=True)
        self.orders_with_single_item = mommy.make('main.Order', items=[self.single_item_sold_multiple_times], make_m2m=True, _quantity=25)

        old_date = timezone.now() - datetime.timedelta(days=60)
        self.old_orders = mommy.make('main.Order', items=[self.single_item_sold_old_orders], make_m2m=True, _quantity=25)
        for order in self.old_orders:
            order.date_placed = old_date
            order.save()

    def test_to_unicode(self):
        self.assertEqual(self.single_item_sold.name, str(self.single_item_sold))

    def test_number_sold(self):
        self.assertEqual(self.single_item_sold.number_sold, 1)
        self.assertEqual(self.single_item_sold_multiple_times.number_sold, 25)
        self.assertEqual(self.single_item_sold_old_orders.number_sold, 25)

    def test_best_selling(self):
        self.assertListEqual(list(Item.get_best_selling()), [self.single_item_sold_multiple_times,
                                                             self.single_item_sold_old_orders, self.single_item_sold])
        self.assertEqual(Item.get_best_selling()[0], self.single_item_sold_multiple_times)
        self.assertEqual(Item.get_best_selling()[1], self.single_item_sold_old_orders)

    def test_best_selling_recently(self):
        self.assertListEqual(list(Item.get_best_selling_recently()), [self.single_item_sold_multiple_times,
                                                                      self.single_item_sold])
