from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Employeur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cashpoint_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - {self.cashpoint_name}"

class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    contact = models.CharField(max_length=50)

    def __str__(self):
        return self.nom

class Produit(models.Model):
    OPERATEURS = [
        ('TELMA', 'Telma'),
        ('ORANGE', 'Orange'),
        ('AIRTEL', 'Airtel'),
    ]
    nom = models.CharField(max_length=100)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    operateur = models.CharField(max_length=10, choices=OPERATEURS)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nom} - {self.operateur}"

class Solde(models.Model):
    cashpoint = models.ForeignKey(Employeur, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, null=True, blank=True)  # Ajout d'une clé étrangère
    operateur = models.CharField(max_length=10, choices=Produit.OPERATEURS)
    montant = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.cashpoint} - {self.produit.nom if self.produit else 'Aucun produit'} - {self.operateur} - {self.montant}"

class Transaction(models.Model):
    OPERATEURS = [
        ('TELMA', 'Telma'),
        ('ORANGE', 'Orange'),
        ('AIRTEL', 'Airtel'),
    ]
    employeur = models.ForeignKey(Employeur, on_delete=models.CASCADE)
    operateur = models.CharField(max_length=10, choices=OPERATEURS)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bonus_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateField(default=now)

    def __str__(self):
        return f"{self.operateur} - {self.montant_total} - {self.bonus_total} - {self.date}"

class Transfert(models.Model):
    OPERATEURS = [
        ('TELMA', 'Telma'),
        ('ORANGE', 'Orange'),
        ('AIRTEL', 'Airtel'),
    ]

    employeur_source = models.ForeignKey(Employeur, related_name='transactions_source', on_delete=models.CASCADE)
    employeur_cible = models.ForeignKey(Employeur, related_name='transactions_cible', on_delete=models.CASCADE)
    operateur = models.CharField(max_length=10, choices=OPERATEURS)
    montant = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.operateur} - {self.montant} de {self.employeur_source.cashpoint_name} à {self.employeur_cible.cashpoint_name}"