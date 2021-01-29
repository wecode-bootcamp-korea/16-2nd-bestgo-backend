from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=45)
    icon_image_url = models.URLField(max_length=2000)

    class Meta:
        db_table = "categories"

class Service(models.Model):
    category  = models.ForeignKey('Category', on_delete=models.CASCADE)
    name      = models.CharField(max_length=100)
    image_url = models.URLField(max_length=2000)
    
    class Meta:
        db_table = "services"

class Request(models.Model):
    user       = models.ForeignKey('users.User', on_delete=models.CASCADE)
    service    = models.ForeignKey('Service', on_delete=models.SET_NULL, null=True)
    region     = models.ForeignKey('users.Region', on_delete=models.CASCADE)
    expired_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "requests"

class Question(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        db_table = "questions"

class QuestionChoice(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    choice   = models.CharField(max_length=200)

    class Meta:
        db_table = "question_choices"

class SelectedChoice(models.Model):
    request = models.ForeignKey('Request', on_delete=models.CASCADE)
    choice  = models.ForeignKey('QuestionChoice', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = "selected_choices"

class RequestMasterMatch(models.Model):
    request = models.ForeignKey('Request', on_delete=models.CASCADE)
    master  = models.ForeignKey('users.Master', on_delete=models.CASCADE)

    class Meta:
        db_table = "request_master_matches"

class Quotation(models.Model):
    match          = models.ForeignKey('RequestMasterMatch', on_delete=models.CASCADE)
    price          = models.DecimalField(max_digits=10, decimal_places=2)
    is_employed    = models.BooleanField(default=False)
    pricing_method = models.ForeignKey('PricingMethod', on_delete=models.CASCADE)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "quotations"

class QuotationImage(models.Model):
    quotation = models.ForeignKey('Quotation', on_delete=models.CASCADE)
    image_url = models.URLField(max_length=2000)

    class Meta:
        db_table = "quotation_images"

class PricingMethod(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "pricing_methods"
