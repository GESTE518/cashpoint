from django.contrib import admin
from django.db.models import Sum
from decimal import Decimal
from .models import Employeur, Fournisseur, Produit, Solde, Transaction, Transfert

class EmployeurAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'cashpoint_name', 
        'total_transferts_envoyes',
        'total_transferts_recus', 
        'total_stock',
    )
    search_fields = ('user__username', 'cashpoint_name')
    list_filter = ('cashpoint_name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            total_initial_stock=Sum('solde__montant'),  # Stock initial de l'employeur
        )
        return qs

    def total_transferts_envoyes(self, obj):
        return obj.transactions_source.aggregate(total=Sum('montant'))['total'] or Decimal(0)
    total_transferts_envoyes.short_description = 'Transferts Envoyés'

    def total_transferts_recus(self, obj):
        return obj.transactions_cible.aggregate(total=Sum('montant'))['total'] or Decimal(0)
    total_transferts_recus.short_description = 'Transferts Reçus'

    def total_stock(self, obj):
        initial_stock = Decimal(obj.total_initial_stock or 0)
        transferts_envoyes = Decimal(self.total_transferts_envoyes(obj))
        transferts_recus = Decimal(self.total_transferts_recus(obj))
        return initial_stock - transferts_envoyes + transferts_recus
    total_stock.short_description = 'Stock Total'


class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'fournisseur', 'operateur', 'total_stock',)
    search_fields = ('nom', 'operateur')
    list_filter = ('operateur', 'fournisseur')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            total_stock=Sum('solde__montant'),  # Total stock lié à Produit via Solde
        )
        return qs

    def total_stock(self, obj):
        return obj.total_stock or Decimal(0)
    total_stock.short_description = 'Stock Total'


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('employeur', 'operateur', 'montant_total', 'bonus_total', 'date')
    list_filter = ('employeur', 'operateur', 'date')
    search_fields = ('employeur', 'operateur', 'montant_total', 'bonus_total', 'date')




      # Pagination et hiérarchie par date
    date_hierarchy = 'date'
    list_per_page = 20

    # Actions d'analyse de données
    actions = ['calculate_total_amount_bonus', 'calculate_avg_amount_bonus', 'filter_by_owner_data']

    # Calculer la somme des montants et bonus pour les dépenses sélectionnées
    def calculate_total_amount_bonus(self, request, queryset):
        total_amount = queryset.aggregate(Sum('montant_total'))['montant_total__sum']
        total_bonus = queryset.aggregate(Sum('bonus_total'))['bonus_total__sum']
        self.message_user(request, f"Montant total: {total_amount}, Bonus total: {total_bonus}")
    calculate_total_amount_bonus.short_description = "Calculer le montant total et le bonus"

    # Analyser les données par `owner` avec filtrage avancé
    def filter_by_owner_data(self, request, queryset):
        selected_owners = queryset.values_list('owner', flat=True).distinct()

        # Collecter les données par `owner`
        filtered_data = {}
        for owner_id in selected_owners:
            owner_name = queryset.filter(owner=owner_id).first().owner.username
            owner_queryset = queryset.filter(owner=owner_id)
            total_amount = owner_queryset.aggregate(Sum('montant_total'))['montant_total__sum']
            total_bonus = owner_queryset.aggregate(Sum('bonus_total'))['bonus_total__sum']
            dates = owner_queryset.dates('date', 'day')

            # Sauvegarder les informations filtrées
            filtered_data[owner_name] = {
                'total_amount': total_amount,
                'total_bonus': total_bonus,
                'dates': list(dates)
            }

        # Affichage des résultats dans l’interface d’administration
        for owner, data in filtered_data.items():
            self.message_user(request, f"Owner: {owner}")
            self.message_user(request, f"  Total Amount: {data['total_amount']}")
            self.message_user(request, f"  Total Bonus: {data['total_bonus']}")
            self.message_user(request, f"  Dates: {data['dates']}")
    filter_by_owner_data.short_description = "Filtrer et analyser les données par propriétaire"






class TransfertAdmin(admin.ModelAdmin):
    list_display = ('employeur_source', 'employeur_cible', 'operateur', 'montant', 'date')
    list_filter = ('operateur', 'employeur_source', 'employeur_cible')
    search_fields = ('employeur_source__user__username', 'employeur_cible__user__username')


class SoldeAdmin(admin.ModelAdmin):
    list_display = ('cashpoint', 'produit', 'operateur', 'montant')
    search_fields = ('cashpoint__user__username', 'produit__nom')
    list_filter = ('operateur', 'cashpoint')


class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'contact')


# Enregistrement des modèles et des configurations d'administrateurs
admin.site.register(Employeur, EmployeurAdmin)
admin.site.register(Fournisseur, FournisseurAdmin)
admin.site.register(Produit, ProduitAdmin)
admin.site.register(Solde, SoldeAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Transfert, TransfertAdmin)
