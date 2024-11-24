
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Customer(models.Model):
    """
    Name: Customer model definition
    """
    name = models.CharField(max_length=132)
    save_by = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Invoice(models.Model):
    """
    Name: Invoice model definition
    Description: 
    author: admin@gmail.com
    """
    INVOICE_TYPE = (
        ('D', ('Dépôt')),
        ('R', ('Retrait')),
        ('T', ('Transfert')),
        ('2', ('2Toi')),
        ('E', ('E-recharge')),
        ('S', ('spide')),
    )

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    save_by = models.ForeignKey(User, on_delete=models.PROTECT)
    invoice_date_time = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(null=True, blank=True)
    invoice_type = models.CharField(max_length=1, choices=INVOICE_TYPE)
    
    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Type_de_tarif"
    
    def __str__(self):
        return f"{self.customer.name}_{self.invoice_type}"
    
class Article(models.Model):
    """
    Name: Article model definition
    Description: 
    Author: admin@gmail.com
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    montant = models.CharField(max_length=32)
    frais = models.IntegerField()
    bonus_operateur = models.DecimalField(max_digits=1000, decimal_places=2, default=0.0)
    bonus_personalise = models.DecimalField(max_digits=1000, decimal_places=2,default=0.0)
    bonus = models.DecimalField(max_digits=1000, decimal_places=2, default=0.0)  # Ajout d'une valeur par défaut ici

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Tarif_pour_les_transaction'

    @property
    def get_bonus(self):
        return self.bonus_operateur + self.bonus_personalise

    def save(self, *args, **kwargs):
        # Calcul automatique du bonus avant de sauvegarder
        self.bonus = self.get_bonus
        super().save(*args, **kwargs)

