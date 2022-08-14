from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import F
import datetime
from cloudinary.models import CloudinaryField

class AbstractInvestment(models.Model):
    offer = models.ForeignKey('Offer', on_delete=models.CASCADE, related_name="investments", null=True, blank=True)

    class Meta:
        abstract=True

class Investor(AbstractUser):
    identity_fin = models.CharField(max_length=50, unique=True)
    contact_num = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=30, unique=True)
    full_name = models.CharField(max_length=50)
    avatar = CloudinaryField('image', default='https://res.cloudinary.com/dn3laf4bh/image/upload/v1647623057/avatar_iu9mmi.svg')
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'username'
    
    def invest(self, startup, summ, offer, curr):
        rates = {
            'USD': 1.7,
            'EUR': 1.73,
            'AZN': 1
        }

        equity = summ * rates[curr] / startup.net_worth
        if offer.available >= equity and InvestorWallet.objects.get(investor=self, curr=curr).balance >= summ and summ >= offer.mis:
            OfferWallet.objects.filter(offer=offer, curr=curr).update(balance = F('balance') + summ)
            InvestorWallet.objects.filter(investor=self, curr=curr).update(balance = F('balance') - summ)
            a = Investment(offer=offer, investor=self, equity=equity, date=datetime.datetime.now())
            a.save()
            offer.available = F('available') - equity
            offer.save()
            if offer.available == 0:
                offer.finish()
            return 0

    def save(self, *args, **kwargs):
        super(Investor, self).save(*args, **kwargs)
        a, b, c = [
            InvestorWallet.objects.filter(curr = 'AZN', balance = 0.0, iban_no = 'AZ9287265392706420', investor = self),
            InvestorWallet.objects.filter(curr = 'USD', balance = 0.0, iban_no = 'AZ9287265392706420', investor = self),
            InvestorWallet.objects.filter(curr = 'EUR', balance = 0.0, iban_no = 'AZ9287265392706420', investor = self)
        ]
        if not a.exists(): InvestorWallet(curr = 'AZN', balance = 0.0, iban_no = 'AZ9287265392706420', investor = self).save()
        if not b.exists(): InvestorWallet(curr = 'USD', balance = 0.0, iban_no = 'AZ9287265392706420', investor = self).save()
        if not c.exists(): InvestorWallet(curr = 'EUR', balance = 0.0, iban_no = 'AZ9287265392706420', investor = self).save()

    def __str__(self):
        return f"{self.username} - {self.identity_fin}"

class InvestorWallet(models.Model):
    curr = models.CharField(max_length=20)
    balance = models.FloatField()
    iban_no = models.CharField(max_length=20)
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name="wallets")
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.investor}'s {self.curr} wallet"

class Startup(models.Model):
    name = models.CharField(max_length=50)
    info = models.CharField(max_length=500, null=True, blank=True)
    net_worth = models.FloatField(null=True, blank=True)
    owned_equity = models.FloatField(null=True, blank=True, default=100.0)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class StartupWallet(models.Model):
    curr = models.CharField(max_length=20)
    balance = models.FloatField()
    iban_no = models.CharField(max_length=20, unique=True)
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="wallets")
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.startup}'s {self.curr} wallet"

class Investment(AbstractInvestment):
    # offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="investments")
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name="investments")
    equity = models.FloatField()
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.startup} - {self.investor}"

class Offer(models.Model):
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="offers")
    total_equity = models.FloatField()
    available = models.FloatField(null=True, blank=True)
    target = models.FloatField(null=True, blank=True)
    mis = models.FloatField(null=True, blank=True) # minimal_investable_sum -- in AZN
    description = models.CharField(max_length=300, null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)
    finished = models.BooleanField(default=False)

    def rollback(self):
        rates = {
            'USD': 1.7,
            'EUR': 1.73,
            'AZN': 1
        }
        currencies = ('AZN', 'USD', 'EUR')
        for curr in currencies:
            offer_investments = Investment.objects.filter(offer=self, curr = curr)
            for offer_investment in offer_investments:
                offer_wallet = OfferWallet.objects.filter(offer=self, curr=curr)
                investor_wallet = InvestorWallet.objects.filter(investor=offer_investment.investor, curr=curr)
                summ = offer_investment.equity * self.startup.net_worth / rates[curr]
                offer_wallet.update(balance = F('balance') - summ)
                investor_wallet.update(balance = F('balance') + summ)
                Investment.objects.delete(offer_investment)
        self.delete()

    def finish(self):
        currencies = ('AZN', 'USD', 'EUR')
        for curr in currencies:
            offer_wallet = OfferWallet.objects.filter(offer = self, curr = curr)
            StartupWallet.objects.filter(startup=self.startup, curr=curr).update(balance = F('balance') + offer_wallet.balance)
            offer_wallet.update(balance=0)
            self.startup.update(owned_equity = F('owned_equity') - self.total_equity)
            self.update(finished=True)

    def save(self, *args, **kwargs):
        self.startup.net_worth = self.target * 100 / self.total_equity
        self.startup.save()
        if not self.available: self.available = self.total_equity
        super(Offer, self).save(*args, **kwargs)
        a, b, c = [
            OfferWallet(curr = 'AZN', balance = 0.0, iban_no = 'AZ9287265392706420', offer = self),
            OfferWallet(curr = 'USD', balance = 0.0, iban_no = 'AZ9287265392706420', offer = self),
            OfferWallet(curr = 'EUR', balance = 0.0, iban_no = 'AZ9287265392706420', offer = self)
        ]
        a.save()
        b.save()
        c.save()

class OfferWallet(models.Model):
    curr = models.CharField(max_length=20)
    balance = models.FloatField()
    iban_no = models.CharField(max_length=20)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="offerwallets")
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.curr} wallet for {self.offer}"