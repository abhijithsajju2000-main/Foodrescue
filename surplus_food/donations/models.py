from django.db import models


from django.conf import settings

import uuid


class BaseClass(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    active_status = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:

        abstract = True


class StatusChoices(models.TextChoices):

    AVAILABLE = 'Available', 'Available'

    COMPLETED = 'Completed', 'Completed'


class FoodDonation(BaseClass):

    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donations')

    food_name = models.CharField(max_length=100)

    description = models.TextField(blank=True, null=True)

    quantity = models.PositiveIntegerField()

    quantity_remaining = models.PositiveIntegerField()

    price = models.FloatField()

    location = models.CharField(max_length=200)

    expiry_time = models.DateTimeField()

    photo = models.ImageField(upload_to='donation-images', blank=True, null=True)

    status = models.CharField(max_length=15, choices=StatusChoices.choices, default=StatusChoices.AVAILABLE)

    class Meta:

        verbose_name = 'Food Donation'

        verbose_name_plural = 'Food Donations'



    def __str__(self):
        return f'{self.food_name} by {self.donor.username} ({self.quantity_remaining} left)'




class FoodClaim(BaseClass):

    donation = models.ForeignKey('FoodDonation', on_delete=models.CASCADE, related_name='claims')

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='claims')

    quantity_claimed = models.PositiveIntegerField(default=1)

    amount_paid = models.FloatField(default=0)

    claimed_at = models.DateTimeField(auto_now_add=True)



    class Meta:

        verbose_name = 'Food Claim'

        verbose_name_plural = 'Food Claims'

    def __str__(self):

        return f'{self.recipient.username} claimed {self.quantity_claimed} x {self.donation.food_name}'