from django.contrib import admin
from django.db.models import Sum, Avg, Count
from .models import Expense, Category

class ExpenseAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = ('owner', 'category', 'description', 'amount', 'bonus', 'date', 'reference')

    # Options de recherche et filtres
    search_fields = ('description', 'category', 'owner__username', 'reference')
    list_filter = ('owner', 'category', 'description', 'date')

    # Pagination et hiérarchie par date
    date_hierarchy = 'date'
    list_per_page = 20

    # Actions d'analyse de données
    actions = ['calculate_total_amount_bonus', 'calculate_avg_amount_bonus', 'filter_by_owner_data']

    # Calculer la somme des montants et bonus pour les dépenses sélectionnées
    def calculate_total_amount_bonus(self, request, queryset):
        total_amount = queryset.aggregate(Sum('amount'))['amount__sum']
        total_bonus = queryset.aggregate(Sum('bonus'))['bonus__sum']
        self.message_user(request, f"Montant total: {total_amount}, Bonus total: {total_bonus}")
    calculate_total_amount_bonus.short_description = "Calculer le montant total et le bonus"

    # Calculer la moyenne des montants et des bonus
    def calculate_avg_amount_bonus(self, request, queryset):
        avg_amount = queryset.aggregate(Avg('amount'))['amount__avg']
        avg_bonus = queryset.aggregate(Avg('bonus'))['bonus__avg']
        self.message_user(request, f"Moyenne des montants: {avg_amount}, Moyenne des bonus: {avg_bonus}")
    calculate_avg_amount_bonus.short_description = "Calculer la moyenne des montants et bonus"

    # Analyser les données par `owner` avec filtrage avancé
    def filter_by_owner_data(self, request, queryset):
        selected_owners = queryset.values_list('owner', flat=True).distinct()

        # Collecter les données par `owner`
        filtered_data = {}
        for owner_id in selected_owners:
            owner_name = queryset.filter(owner=owner_id).first().owner.username
            owner_queryset = queryset.filter(owner=owner_id)
            total_amount = owner_queryset.aggregate(Sum('amount'))['amount__sum']
            total_bonus = owner_queryset.aggregate(Sum('bonus'))['bonus__sum']
            categories = owner_queryset.values('category').annotate(count=Count('category'))
            descriptions = owner_queryset.values('description').annotate(count=Count('description'))
            dates = owner_queryset.dates('date', 'day')

            # Sauvegarder les informations filtrées
            filtered_data[owner_name] = {
                'total_amount': total_amount,
                'total_bonus': total_bonus,
                'categories': list(categories),
                'descriptions': list(descriptions),
                'dates': list(dates)
            }

        # Affichage des résultats dans l’interface d’administration
        for owner, data in filtered_data.items():
            self.message_user(request, f"Owner: {owner}")
            self.message_user(request, f"  Total Amount: {data['total_amount']}")
            self.message_user(request, f"  Total Bonus: {data['total_bonus']}")
            self.message_user(request, f"  Categories: {data['categories']}")
            self.message_user(request, f"  Descriptions: {data['descriptions']}")
            self.message_user(request, f"  Dates: {data['dates']}")
    filter_by_owner_data.short_description = "Filtrer et analyser les données par propriétaire"

admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Category)
