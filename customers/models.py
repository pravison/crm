from django.db import models
from tinymce.models import HTMLField
from clients.models import Client, Staff

# Create your models here.
class CustomerNicheSegment(models.Model):
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='Niches')
    segment = models.CharField(max_length=200, help_text="think of this as diffrent niches customer can be")
    outreach_message = models.TextField(max_length=700, help_text="this message must be created first on facebook then be approved, if not approved whatsapp wont send them")
    def __str__(self):
        return self.segment
    
class Customer(models.Model):
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='customers')
    name = models.CharField(max_length=200, blank=True, null=True)
    whatsapp_profile = models.CharField(max_length=200, blank=True, null=True)
    funnel_stage = models.CharField(max_length=50, default='interest', choices=(('awareness', 'awareness'), ('interest', 'interest'),('decision', 'decision'), ('purchase', 'purchase'), ('active', 'active'), ('dormant', 'dormant'))) # active for active customer and dormant for dormant customer
    niche = models.ForeignKey(CustomerNicheSegment, null=True, blank=True, on_delete=models.SET_NULL, help_text='customer niche segments')
    phone_number = models.CharField(max_length=20, help_text="must write your number in international formart including you country code and excluding (+) example 254765342134 makesure it doesnt have + sign")
    email = models.EmailField( blank=True, null=True)
    description = HTMLField(blank=True, null=True)
    last_interaction_summary = HTMLField(blank=True, null=True)
    refferal_source = models.CharField(max_length=100, default='shop', choices=(('shop', 'shop'), ('call', 'call'), ('facebook', 'facebook'), ('friend', 'friend'), ('online', 'online')), help_text='how customer found out about us')
    date_added = models.DateTimeField(auto_now_add = True)
    last_talked = models.DateField(auto_now_add=True, blank=True, null=True)


    def __str__(self):
        customer_name = self.name if self.name else self.phone_number
        return f" {customer_name}"
    
class Conversation(models.Model):
    client  = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='coversations')
    staff = models.ForeignKey(Staff, null=True, blank=True, on_delete=models.SET_NULL, related_name='coversations')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True, related_name='conversations')
    sender = models.CharField(max_length=50, choices=(('customer', 'customer'), ('AI', 'AI')))
    message = models.TextField()
    read = models.BooleanField(default=False)
    date_added = models.DateField(auto_now_add = True, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"

class CustomerHistory(models.Model):
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='historys')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    product =  models.CharField(max_length=100, blank=True, null=True)
    CUSTOMER_HISTORY_CHOICES={
        'view': 'view',
        'add to cart' : 'add to cart',
        'purchased' : 'purchased'
    } 
    history_status = models.CharField(max_length=100, default='view', choices=CUSTOMER_HISTORY_CHOICES)
    date = models.DateField(auto_now_add=True)
    time= models.TimeField(auto_now_add=True)

    def __str__(self):
        return f' {self.date} @ {self.time}'

class Interaction(models.Model):
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='interactions')
    staff = models.ForeignKey(Staff, null=True, blank=True, on_delete=models.SET_NULL, related_name='interactions')
    interaction_place = models.CharField(max_length=50, choices=(('your shop', 'your shop'), ('customers shop', 'customers shop'), ('call', 'call'), ('online meeting', 'online meeting')), help_text='where was the interaction held')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    customer_sales_funnel_stage = models.CharField(max_length=100, blank=True, null=True, choices=(('awareness', 'awareness'), ('interest', 'interest'),('decision', 'decision'), ('purchase', 'purchase'), ('active', 'active'), ('dormant', 'dormant')))
    conversation_summary = HTMLField(max_length=1000, blank=True, null=True)
    next_step = models.CharField(max_length=300)
    next_step_date = models.DateField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        customer_name = self.customer.name if self.customer.name else self.customer.phone_number
        return f'{customer_name}'



class NewsletterSubscription(models.Model):
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='subscriptions')
    customer_name = models.CharField(max_length=200)
    whatsapp_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField()

    def __str__(self):
        return self.customer_name

class Testimonial(models.Model): 
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='testimonials')
    customer_name = models.CharField(max_length=200)
    profile_image = models.ImageField(upload_to='customers', null=True, blank=True)
    customer_tag =models.CharField(max_length=100, null=True, blank=True )
    product =models.CharField(max_length=100, null=True, blank=True)
    number_of_stars = models.IntegerField(default=5)
    message = HTMLField()
    approved = models.BooleanField(default=True, help_text='check this if you want testimony to appear on website')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_name
        
    @property
    def imageURL(self):
        try:
            url = self.profile_image.url
        except:
            url = ''
        return url

class Comment(models.Model): 
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='comments')  
    customer_name = models.CharField(max_length=200)
    email = models.EmailField(null=True, blank=True)
    product =  models.CharField(max_length=200, blank=True, null=True)
    profile_image = models.ImageField(upload_to='customers', null=True, blank=True)
    message = HTMLField()
    useful_count = models.IntegerField(default=0, help_text='number of likes')
    not_useful_count = models.IntegerField(default=0, help_text='if this number exceeds 10 we remove the comment from appearing to the website')
    useful = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_name
        
    @property
    def imageURL(self):
        try:
            url = self.profile_image.url
        except:
            url = ''
        return url

class CustomerMessage(models.Model):
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL, related_name='messages') 
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    message = HTMLField()
    replied = models.BooleanField(default=False)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name