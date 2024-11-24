from django.contrib import admin
from .models import Customer, Invoice, Article
from django.utils.translation import gettext_lazy as _

# Register your models here.

class AdminCustomer(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class AdminInvoice(admin.ModelAdmin):
    list_display = ('customer', 'invoice_type', 'save_by')
    # Utilisez "customer__name" et "save_by__username" pour faire des recherches sur des ForeignKeys
    search_fields = ('customer__name', 'invoice_type', 'save_by__username',)

class AdminArticle(admin.ModelAdmin):
    list_display = (
        'invoice', 
        'montant',    
        'frais', 
        'bonus_operateur', 
        'bonus_personalise',
        'bonus', 
    )
    # Utilisez "invoice__customer__name" pour faire des recherches dans la relation ForeignKey
    search_fields = (
        'invoice__customer__name', 
        'montant',    
        'frais', 
        'bonus_operateur', 
        'bonus_personalise',
        'bonus', 
    )

admin.site.register(Customer, AdminCustomer)
admin.site.register(Invoice, AdminInvoice)
admin.site.register(Article, AdminArticle)

admin.site.site_title = _("SYSTEME DE GESTION DES CASHPOINT")
admin.site.site_header = _("SYSTEME DE GESTION DES CASHPOINT")
admin.site.index_title = _("SYSTEME DE GESTION DES CASHPOINT")
