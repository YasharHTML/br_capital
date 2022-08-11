from django.contrib import admin
from .models import *

admin.site.register(Investor)
admin.site.register(InvestorWallet)
admin.site.register(Startup)
admin.site.register(StartupWallet)
admin.site.register(Investment)
admin.site.register(Offer)
admin.site.register(OfferWallet)