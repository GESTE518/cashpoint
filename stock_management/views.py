from django.shortcuts import render, get_object_or_404, redirect
from .models import Produit, Transaction, Employeur, Transfert, Fournisseur
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.timezone import now
from decimal import Decimal

# Vue pour afficher le stock des produits
@login_required
def afficher_stock(request):
    produits = Produit.objects.all()
    return render(request, 'stock_management/stock_list.html', {'produits': produits})

# Vue pour afficher toutes les transactions et transferts
@login_required
def afficher_transactions_et_transferts(request):
    transactions = Transaction.objects.all()  # Récupère toutes les transactions
    transferts = Transfert.objects.all()  # Récupère tous les transferts
    return render(request, 'stock_management/transaction_et_transfert_list.html', {'transactions': transactions, 'transferts': transferts})


# Vue pour afficher les transactions sans référence aux soldes
@login_required
def afficher_soldes(request):
    # Récupérer les transactions de l'employeur ou de l'utilisateur
    transactions = Transaction.objects.all()  # On remplace Solde par Transaction si nécessaire
    return render(request, 'stock_management/solde_list.html', {'transactions': transactions})

# Vue pour ajouter une transaction (sans lien avec les soldes)
@login_required
def ajouter_transaction(request):
    if not hasattr(request.user, 'employeur'):
        return HttpResponse("Vous devez être associé à un employeur pour effectuer des transactions.")

    employeur = request.user.employeur

    if request.method == 'POST':
        operateur = request.POST.get('operateur')
        montant = Decimal(request.POST.get('montant'))
        bonus = Decimal(request.POST.get('bonus', '0.00'))
        
        montant_total = montant

        # Création de la transaction sans mise à jour du stock
        Transaction.objects.create(
            employeur=employeur,
            operateur=operateur,
            montant_total=montant_total,
            bonus_total=bonus,
            date=now()
        )

        return redirect('afficher_transactions_et_transferts')

    return render(request, 'stock_management/ajouter_transaction.html')

# Vue pour transférer des fonds entre employeurs (sans mise à jour des soldes)
@login_required
def transferer_fonds(request):
    # Vérifie si l'utilisateur a un employeur associé
    try:
        employeur_source = request.user.employeur
    except Employeur.DoesNotExist:
        return HttpResponse("Vous devez être associé à un employeur pour effectuer des transferts de fonds.")

    if request.method == 'POST':
        cible_id = request.POST.get('cible_id')
        operateur = request.POST.get('operateur')
        montant = Decimal(request.POST.get('montant'))

        employeur_cible = get_object_or_404(Employeur, id=cible_id)

        # Crée un transfert sans mise à jour des soldes de stock
        Transfert.objects.create(
            employeur_source=employeur_source,
            employeur_cible=employeur_cible,
            operateur=operateur,
            montant=montant
        )

        return redirect('afficher_soldes')

    employeurs = Employeur.objects.exclude(id=employeur_source.id)
    return render(request, 'stock_management/transferer_fonds.html', {'employeurs': employeurs})

# Vue pour afficher la liste des fournisseurs
@login_required
def liste_fournisseurs(request):
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'stock_management/fournisseur_list.html', {'fournisseurs': fournisseurs})

# Vue pour afficher les détails d'un fournisseur
@login_required
def details_fournisseur(request, fournisseur_id):
    fournisseur = get_object_or_404(Fournisseur, id=fournisseur_id)
    return render(request, 'stock_management/fournisseur_detail.html', {'fournisseur': fournisseur})

# Vue d'accueil
@login_required
def index(request):
    return render(request, 'stock_management/index.html')
