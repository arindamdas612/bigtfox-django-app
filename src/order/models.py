from django.db import models
from django.db.models.deletion import CASCADE
from django.utils import timezone

from user.models import User
from shop.models import Product


class Order(models.Model):
    class Meta:
        verbose_name_plural = "Orders"
    STATUS_CHOICE = (
        ('CR', 'Created'),
        ('PL', 'Placed'),
        ('CU', 'Cancelled By User'),
        ('CN', 'Cancelled'),
        ('PK', 'Packed'),
        ('TN', 'In Transit'),
        ('DV', 'Delivered'),
        ('RI', 'Return Initiated'),
        ('RC', 'Return Completed'),
        ('FL', 'Failed'),
    )

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True, related_name='order_owner')

    name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=15)

    shipping = models.TextField(max_length=500)
    billing = models.TextField(max_length=500)

    status = models.CharField(max_length=2, choices=STATUS_CHOICE)

    item_total = models.FloatField()
    discount = models.FloatField()
    tax = models.FloatField()
    grand_total = models.FloatField()

    notes = models.TextField(max_length=500)

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Order, self).save(*args, **kwargs)


class OrderActivity(models.Model):
    class Meta:
        verbose_name_plural = "Order Activities"
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    from_status = models.CharField(max_length=2, null=True, blank=True)
    to_status = models.CharField(max_length=2)

    created = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        return super(OrderActivity, self).save(*args, **kwargs)


class OrderItem(models.Model):
    class Meta:
        verbose_name_plural = "Order Items"
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField()

    unit_price = models.FloatField()

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(OrderItem, self).save(*args, **kwargs)


class OrderPayment(models.Model):
    class Meta:
        verbose_name_plural = "Order Payments"

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    rp_payment_id = models.CharField(max_length=200)
    rp_order_id = models.CharField(max_length=200)

    success = models.BooleanField()

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(OrderPayment, self).save(*args, **kwargs)


class OrderRefund(models.Model):
    class Meta:
        verbose_name_plural = "Order Refunds"
    STATUS_CHOICE = (
        ('RI', 'Refund Initated'),
        ('RC', 'Refund Completed'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    refund_status = models.CharField(max_length=2, choices=STATUS_CHOICE)

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(OrderRefund, self).save(*args, **kwargs)
