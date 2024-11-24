from django.urls import path
from . import views

urlpatterns = [
    path('', views.afficher_transactions_et_transferts, name='afficher_transactions_et_transferts'),# Page d'accueil
    path('stock/', views.afficher_stock, name='afficher_stock'),  # Affichage des stocks de produits
    path('soldes/', views.afficher_soldes, name='afficher_soldes'),  # Affichage des soldes
    path('transaction/ajouter/', views.ajouter_transaction, name='ajouter_transaction'),  # Ajout de transaction
    path('transferer_fonds/', views.transferer_fonds, name='transferer_fonds'),  # Transfert de fonds entre employeurs
    path('fournisseurs/', views.liste_fournisseurs, name='liste_fournisseurs'),  # Liste des fournisseurs
    path('fournisseurs/<int:fournisseur_id>/', views.details_fournisseur, name='details_fournisseur'),  # Détails d'un fournisseur
   
]
