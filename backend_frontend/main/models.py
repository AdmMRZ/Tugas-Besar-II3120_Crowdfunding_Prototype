from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

CATEGORY_CHOICES = [
    ('MEDICAL', 'Medical & Health'),
    ('EDUCATION', 'Education'),
    ('DISASTER', 'Disaster Relief'),
    ('HUMANITY', 'Humanity'),
    ('ANIMAL', 'Animal Welfare'),
    ('RELIGIOUS', 'Religious'),
]

class Campaign(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='MEDICAL')
    description = models.TextField()
    target_amount = models.IntegerField()
    current_amount = models.IntegerField(default=0)
    deadline = models.DateTimeField()
    image_url = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def progress_percentage(self):
        if self.target_amount > 0:
            return int((self.current_amount / self.target_amount) * 100)
        return 0

class Donation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('FLAGGED', 'Flagged as Fraud'),
    ]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='donations')
    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    message = models.TextField(blank=True, null=True)
    donated_at = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    risk_score = models.IntegerField(default=0)
    risk_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.donor.username} - {self.amount} [{self.status}]"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return f"Saldo {self.user.username}: Rp {self.balance}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
