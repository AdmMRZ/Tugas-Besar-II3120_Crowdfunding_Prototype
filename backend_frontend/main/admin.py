from django.contrib import admin
from .models import Campaign, Donation, UserProfile

class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'target_amount', 'current_amount', 'deadline')
    search_fields = ('title', 'description')

class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'amount', 'campaign', 'donated_at')
    list_filter = ('donated_at',)
    
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')
    search_fields = ('user__username',)

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(Donation, DonationAdmin)

admin.site.site_header = "CrowdFund Super Admin"
admin.site.site_title = "CrowdFund Portal"
admin.site.index_title = "Welcome to Manager Area"
