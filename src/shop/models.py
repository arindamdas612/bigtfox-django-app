from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.utils import timezone

from user.models import User

# Create your models here.


class AttributeMaster(models.Model):
    class Meta:
        verbose_name_plural = "Attribute Masters"
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=20)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='AtM_creator')
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='AtM_modifier')

    def __str__(self):
        return f'{self.name} - {self.type}'

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(AttributeMaster, self).save(*args, **kwargs)


class AttributeValue(models.Model):

    class Meta:
        verbose_name_plural = "Attribute Values"

    attribute_master = models.ForeignKey(
        AttributeMaster, on_delete=models.CASCADE)
    display_value = models.CharField(max_length=50)

    total_codes = models.IntegerField(default=0)
    color_abbr = models.CharField(max_length=2, null=True, blank=True)

    code_1 = models.CharField(max_length=50, null=True, blank=True)
    code_2 = models.CharField(max_length=50, null=True, blank=True)
    code_3 = models.CharField(max_length=50, null=True, blank=True)
    code_4 = models.CharField(max_length=50, null=True, blank=True)

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='AtV_creator')
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='AtV_modifier')

    def __str__(self):
        return f'{self.attribute_master.name}|{self.display_value}|{self.total_codes} code(s)'

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(AttributeValue, self).save(*args, **kwargs)


class PrimaryCategory(models.Model):

    class Meta:
        verbose_name_plural = "Primary Categories"
    MEN = 'Men'
    WOMEN = 'Women'
    KIDS = 'Kids'
    GENDER_CHOICES = [
        (MEN, 'Men'),
        (WOMEN, 'Women'),
        (KIDS, 'Kids')
    ]

    name = models.CharField(max_length=30)
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, default=MEN)
    display_order = models.IntegerField(default=1)
    abr = models.CharField(max_length=4)

    slug = models.SlugField(unique=True, blank=True)

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='pCat_creator')
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pCat_modifier')

    def __str__(self):
        return f"{self.gender}'s {self.name}"

    def clean_fields(self, exclude=None):
        super(PrimaryCategory, self).clean_fields(exclude)

        if not self.id:
            same_order_hcl = PrimaryCategory.objects.filter(
                display_order=self.display_order).first()
            if same_order_hcl:
                raise ValidationError(
                    ({'display_order': ['Duplicate Display Order']}))

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        self.slug = slugify(f"{self.gender} {self.name}")

        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(PrimaryCategory, self).save(*args, **kwargs)


class Category(models.Model):
    class Meta:
        verbose_name_plural = "Categories"

    p_cat = models.ForeignKey(
        PrimaryCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    abr = models.CharField(max_length=4)

    slug = models.SlugField(unique=True, blank=True)

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='cat_creator')
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cat_modifier')

    def __str__(self):
        return f"{self.p_cat}-{self.name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.p_cat.slug} {self.name}")
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Category, self).save(*args, **kwargs)


class Brand(models.Model):
    class Meta:
        verbose_name_plural = "Brands"

    name = models.CharField(max_length=30)
    abr = models.CharField(max_length=4, unique=True)
    third_party_brand = models.BooleanField(default=True)

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='brand_creator')
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='brand_modifier')

    def __str__(self):
        text = 'Own' if not self.third_party_brand else 'Other'
        return f'{self.name} ({text})'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Brand, self).save(*args, **kwargs)


class Product(models.Model):
    class Meta:
        verbose_name_plural = "Products"

    title = models.CharField(max_length=80)

    legacy_sku = models.CharField(max_length=50, null=True, blank=True)
    code = models.CharField(max_length=3)

    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True)

    description = models.TextField(max_length=500)
    listing_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    qty = models.IntegerField()
    maximum_retail_price = models.FloatField()
    listing_price = models.FloatField()
    tax = models.FloatField()

    additional_discount = models.FloatField(default=0.0)
    slug = models.SlugField(max_length=100)

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='prd_creator')
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='prd_modifier')

    def save(self, *args, **kwargs):
        slug = slugify(f"{self.category.slug} {self.title}")
        self.slug = slug
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Product, self).save(*args, **kwargs)


class ProductSKU(models.Model):
    class Meta:
        verbose_name_plural = "Product SKU"

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="system_sku")
    sku = models.CharField(max_length=40, unique=True,
                           blank=True, null=True)

    def generate_sku(self):
        prefernece_list = ['COLOR', 'SIZE', 'FOOTSIZE']
        brand = self.product.brand.abr
        code = self.product.code
        p_cat = self.product.category.p_cat.abr
        cat = self.product.category.abr

        sku_dynamic = ''
        for prefernece in prefernece_list:
            attribute_value = ProductAttribute.objects.filter(
                attribute__attribute_master__type=prefernece, product=self.product).first()

            print(attribute_value, prefernece)
            if attribute_value:
                if prefernece == 'COLOR':
                    sku_dynamic = sku_dynamic + attribute_value.attribute.color_abbr
                elif prefernece == 'FOOTSIZE':
                    size = attribute_value.attribute.display_value
                    text = f'0{size}' if len(size) == 1 else size
                    sku_dynamic = sku_dynamic + str(text)
                else:
                    sku_dynamic = sku_dynamic + attribute_value.attribute.display_value

        sku_dynamic = sku_dynamic.upper()

        generated_sku = f"{brand}_{code}_{p_cat}{cat}_{sku_dynamic}"
        return generated_sku

    def get_parent_sku(self):
        return self.sku

    def save(self, *args, **kwargs):
        self.sku = self.generate_sku()
        super(ProductSKU, self).save(*args, **kwargs)


class ProductAttribute(models.Model):

    class Meta:
        verbose_name_plural = "Product Attributes"

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_attributes")
    attribute = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)

    def clean_fields(self, exclude=None):
        super(ProductAttribute, self).clean_fields(exclude)

        if not self.id:
            attribute = ProductAttribute.objects.filter(
                attribute__attribute_master__type=self.attribute.attribute_master.type, product=self.product).first()
            if attribute:
                raise ValidationError(
                    ({'attribute': ['Cannot Add Duplicate attributes types']}))

    def __str__(self):
        return f'{self.product.title} - {self.attribute}'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(ProductAttribute, self).save(*args, **kwargs)


class ProductImage(models.Model):

    class Meta:
        verbose_name_plural = "Product Images"
    # todo Change to AWS S3 upload images
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='images')
    is_cover = models.BooleanField(default=False)
    image_link = models.TextField(max_length=300)

    display_order = models.IntegerField(default=0)

    def __str__(self):
        second_text = 'Cover' if self.is_cover else 'Other'
        return f"{self.product} - {second_text} @ {self.display_order}"

    def clean_fields(self, exclude=None):
        if self.is_cover:
            self.display_order = 0

        super(ProductImage, self).clean_fields(exclude)

        if not self.id:
            product_order_image = ProductImage.objects.filter(
                display_order=self.display_order, product=self.product).first()
            if product_order_image:
                if self.is_cover:
                    raise ValidationError(({'is_cover': [
                        'Cover Image for this Image is already set. Only one cover Image per Product']}))
                else:
                    raise ValidationError(({'display_order': [
                                            'Image of this product with same Display Order already exists, please change the DO.']}))


class SharedImage(models.Model):
    class Meta:
        verbose_name_plural = "Shared Images"

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='child_product')
    parent_product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='parent_product')


class ProductTag(models.Model):
    class Meta:
        verbose_name_plural = "Product Tags"

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    tag = models.SlugField()

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='prdTag_creator')
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='prdTag_modifier')

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(ProductTag, self).save(*args, **kwargs)

    def __str__(self):
        return f'@{self.tag} {self.product.title}'


class ProductReview(models.Model):
    parent_sku = models.CharField(max_length=20)

    user_rating = models.DecimalField(max_digits=2, decimal_places=1)
    user_review = models.TextField(max_length=600)

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='review_creator')
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='review_modifier')

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(ProductReview, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.parent_sku} {self.user_rating}'


class ReviewReaction(models.Model):
    review = models.ForeignKey(ProductReview, on_delete=models.CASCADE)

    reaction = models.BooleanField(default=True)

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='revReaction_creator')
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='revReaction_modifier')

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(ReviewReaction, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.review} {"Like" if self.reaction else "Dslike"}'
