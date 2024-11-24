from django.shortcuts import render
from django.views import View
from .models import Customer, Invoice, Article
from django.contrib import messages
from django.http import HttpResponse
import pdfkit
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import get_template
from django.db import transaction
from .utils import pagination, get_invoice
from .decorators import superuser_required
from django.utils.translation import gettext as _

class HomeView(LoginRequiredMixin, View):
    """ Main view """
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        invoices = Invoice.objects.select_related('customer', 'save_by').all().order_by('-invoice_date_time')
        items = pagination(request, invoices)
        context = {'invoices': items}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Modification d'une facture
        if request.POST.get('id_modified'):
            try:
                obj = Invoice.objects.get(id=request.POST.get('id_modified'))
                obj.paid = request.POST.get('modified') == 'True'
                obj.save()
                messages.success(request, _("Change made successfully."))
            except Exception as e:
                messages.error(request, f"Sorry, the following error has occurred: {e}.")

        # Suppression d'une facture
        if request.POST.get('id_supprimer'):
            try:
                obj = Invoice.objects.get(pk=request.POST.get('id_supprimer'))
                obj.delete()
                messages.success(request, _("The deletion was successful."))
            except Exception as e:
                messages.error(request, f"Sorry, the following error has occurred: {e}.")

        invoices = Invoice.objects.select_related('customer', 'save_by').all().order_by('-invoice_date_time')
        items = pagination(request, invoices)
        context = {'invoices': items}
        return render(request, self.template_name, context)

class AddCustomerView(LoginRequiredMixin, View):
    """ Add new customer """
    template_name = 'add_customer.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        data = {'name': request.POST.get('name'), 'save_by': request.user}
        try:
            created = Customer.objects.create(**data)
            if created:
                messages.success(request, "Customer registered successfully.")
            else:
                messages.error(request, "Sorry, please try again. The data sent is corrupt.")
        except Exception as e:
            messages.error(request, f"Sorry, our system is detecting the following issue: {e}.")
        return render(request, self.template_name)

class AddInvoiceView(LoginRequiredMixin, View):
    """ Add a new invoice view """
    template_name = 'add_invoice.html'

    def get(self, request, *args, **kwargs):
        customers = Customer.objects.all()
        context = {'customers': customers}
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        items = []
        try:
            customer = request.POST.get('customer')
            invoice_type = request.POST.get('invoice_type')
            articles = request.POST.getlist('article')
            montant = request.POST.getlist('montant')
            frais = request.POST.getlist('frais')
            bonus_operateur = request.POST.getlist('bonus_operateur')
            bonus_personalise = request.POST.getlist('bonus_personalise')
            bonus_a = request.POST.getlist('bonus-a')

            bonus = request.POST.get('bonus')

            # Création de la facture
            invoice_data = {
                'customer_id': customer,
                'save_by': request.user,
                'invoice_type': invoice_type,
            }
            invoice = Invoice.objects.create(**invoice_data)

            # Création des articles associés
            for index in range(len(articles)):
                item = Article(
                    invoice=invoice,
                    montant=montant[index],
                    frais=int(frais[index]),
                    bonus_operateur=bonus_operateur[index],
                    bonus_personalise=bonus_personalise[index],
                    bonus = bonus_a[index],
                )
                items.append(item)

            Article.objects.bulk_create(items)
            messages.success(request, "Data saved successfully.")

        except Exception as e:
            messages.error(request, f"Sorry, the following error has occurred: {e}.")

        customers = Customer.objects.all()
        context = {'customers': customers}
        return render(request, self.template_name, context)

class InvoiceVisualizationView(LoginRequiredMixin, View):
    """ View for visualizing an invoice """
    template_name = 'invoice.html'

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        context = get_invoice(pk)
        return render(request, self.template_name, context)

@superuser_required
def get_invoice_pdf(request, *args, **kwargs):
    """ Generate a PDF file from an HTML template """
    pk = kwargs.get('pk')
    context = get_invoice(pk)
    context['date'] = datetime.datetime.today()

    # Charger le fichier HTML
    template = get_template('invoice-pdf.html')

    # Rendu du HTML avec les variables de contexte
    html = template.render(context)

    # Options pour le format du PDF
    options = {
        'page-size': 'Letter',
        'encoding': 'UTF-8',
        "enable-local-file-access": ""
    }

    # Générer le PDF
    pdf = pdfkit.from_string(html, False, options)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = "attachment; filename='invoice.pdf'"

    return response
