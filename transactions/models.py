from sre_parse import CATEGORIES
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now 

# Create your models here.


class Expense(models.Model):
    DESCRIPTION= (
        ('D', ('Dépôt')),
        ('R', ('Retrait')),
        ('T', ('Transfert')),
        ('2', ('2Toi')),
        ('E', ('E-recharge')),
        ('S', ('spide')),
    )

    amount = models.FloatField()
    date = models.DateField(default=now)
    description = models.CharField(max_length=1, choices=DESCRIPTION)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    category = models.CharField(max_length=266)
    bonus = models.FloatField(default=0.0)  # Ajout d'une valeur par défaut
    reference = models.CharField(max_length=32, default='N/A') 

    def __str__(self):
        return self.category
    class Meta:
        ordering:['-date']
        verbose_name_plural = 'transactions'
class Category(models.Model):
        name = models.CharField(max_length=255)

        class Meta:
            verbose_name_plural = 'Categories'
        def __str__(self):
               return self.name 