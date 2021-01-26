from django.db import models

class User(models.Model):
    name          = models.CharField(max_length=45)
    email         = models.EmailField(max_length=60, unique=True)
    password      = models.CharField(max_length=100)
    phone_number  = models.CharField(max_length=11, unique=True, null=True)
    is_master     = models.BooleanField(default=False)
    gender        = models.ForeignKey('Gender', null=True, on_delete=models.SET_NULL)
    profile_image = models.URLField(max_length=2000, null=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"

class Master(models.Model):
    user            = models.ForeignKey('User', on_delete=models.CASCADE)
    introduction    = models.CharField(max_length=100)
    birthdate       = models.DateField()
    career          = models.IntegerField(null=True)
    description     = models.TextField(null=True)
    master_regions  = models.ManyToManyField('Region', related_name='master_region', through='Area')
    master_payments = models.ManyToManyField('Payment', related_name='master_payment', through='MasterPayment')
    reviews         = models.ManyToManyField('User', related_name='user_review', through='Review')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "masters"

class MasterService(models.Model):
    master  = models.ForeignKey('Master', on_delete=models.CASCADE)
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE)
    is_main = models.BooleanField(default=False)

    class Meta:
        db_table = "master_services"

class Review(models.Model):
    user      = models.ForeignKey('User', on_delete=models.CASCADE)
    master    = models.ForeignKey('Master', related_name='master_review', on_delete=models.CASCADE)
    rating    = models.DecimalField(max_digits=2, decimal_places=1)
    image_url = models.URLField(max_length=2000, null=True)
    content   = models.TextField(null=True)

    class Meta:
        db_table = "reviews"

class Region(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "regions"

class Area(models.Model):
    region = models.ForeignKey('Region', on_delete=models.CASCADE)
    master = models.ForeignKey('Master', on_delete=models.CASCADE)

    class Meta:
        db_table = "areas"

class Certificate(models.Model):
    master    = models.ForeignKey('Master', on_delete=models.CASCADE)
    image_url = models.URLField(max_length=2000)

    class Meta:
        db_table = "certificates"

class Payment(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "payments"

class MasterPayment(models.Model):
    master  = models.ForeignKey('Master', on_delete=models.CASCADE)
    payment = models.ForeignKey('Payment', on_delete=models.CASCADE)

    class Meta:
        db_table = "master_payments"

class Gender(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = "genders"