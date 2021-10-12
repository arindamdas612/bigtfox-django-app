from django.db import models
from django.utils import timezone

from user.models import User
from shop.models import Product


class Cart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    guest_code = models.CharField(max_length=20, blank=True, null=True)
    total_items = models.IntegerField()

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def is_guest(self):
        return True if self.guest_code else False

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Cart, self).save(*args, **kwargs)


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='cart_items')

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField()

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def is_guest(self):
        return self.cart.is_guest

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(CartItem, self).save(*args, **kwargs)
