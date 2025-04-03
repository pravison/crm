from django.db import models
from tinymce.models import HTMLField  
from django.contrib.auth.models import User

# Create your models here.
class Industry(models.Model):
    name = models.CharField(max_length=200)
    prompt = HTMLField( null=True, blank=True)

    def __str__(self) :
        return self.name

class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=200)
    profile_image = models.ImageField(upload_to='profile/', null=True, blank=True)
    business_name = models.CharField(max_length=200, unique=True)
    business_pitch = models.CharField(max_length=200, null=True, blank=True)
    business_logo = models.ImageField(upload_to='logo/', null=True, blank=True)
    slug = models.CharField(max_length=200, unique=True)
    custom_domain = models.CharField(max_length=200, blank=True, null=True, unique=True)
    created_on = models.DateField(auto_now_add=True)
    email = models.EmailField(blank=True, null=True)
    industry = models.ForeignKey(Industry, null=True, blank=True, on_delete=models.SET_NULL)
    phone_number = models.CharField(max_length=16, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=16, blank=True, null=True)
    refferal_code = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    business_address = models.CharField(max_length=200, blank=True, null=True)
    facebook_link = models.URLField(blank=True, null=True)
    x_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)
    linkedln_link = models.URLField(blank=True, null=True)
    youtube_link = models.URLField(blank=True, null=True)
    tiktok_link = models.URLField(blank=True, null=True)

    def __str__(self) :
        return self.business_name
    
    @property
    def imageURL(self):
        try:
            url = self.profile_image.url
        except:
            url = ''
        return url


class PageVisit(models.Model):
    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField()
    session_key = models.CharField(max_length=40, unique=True)
    visit_count = models.PositiveIntegerField(default=1)
    last_visit = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"IP: {self.ip_address} | Visits: {self.visit_count}"

class  Staff(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE, related_name='staff')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=300)
    profile_image = models.ImageField(upload_to='teams', blank=True, null=True)
    role = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=17, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=17, blank=True, null=True, help_text='makes usre you use international format and exclude + e.g 254765432388 if you do write your number this way whatsapp link wont work')
    email = models.EmailField( blank=True, null=True)
    facebook_link = models.URLField(blank=True, null=True)
    x_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)
    linkedln_link = models.URLField(blank=True, null=True)
    youtube_link = models.URLField(blank=True, null=True)
    tiktok_link = models.URLField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f'{self.user.username}'
    
    @property
    def imageURL(self):
        try:
            url = self.profile_image.url
        except:
            url = ''
        return url


class FAQ(models.Model):
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='faqs')
    question = models.CharField(max_length=200)
    answer = HTMLField()
    staff_only = models.BooleanField(default=False)

    def __str__(self):
        return self.question

class TermsAndPolicy(models.Model):
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='policies')
    terms_and_policy = HTMLField(default="By using our platform, you agree to the terms of this privacy policy. If you do not agree with these terms, please do not use the platform.")

    def __str__(self):
        return self.terms_and_policy[:100]