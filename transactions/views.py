from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
import datetime
import csv
import xlwt
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum

from django.utils import timezone

from django.db.models import Sum

# Create your views here.

def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)

def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    user = request.user

    context = {
        'expenses': expenses,
        'page_obj': page_obj,
    }
    return render(request, 'transactions/index.html', context)

def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }

    if request.method == 'GET':
        return render(request, 'transactions/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        bonus = request.POST.get('bonus', 0.0)  # Récupérer le bonus
        reference = request.POST['reference']  # Récupérer la référence

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'transactions/add_expense.html', context)

        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'transactions/add_expense.html', context)

        Expense.objects.create(owner=request.user, amount=amount, date=date,
                               category=category, description=description,
                               bonus=bonus, reference=reference)  # Inclure bonus et reference
        messages.success(request, 'Transaction est succès')

        return redirect('transactions')

def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }

    if request.method == 'GET':
        return render(request, 'transactions/edit-expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        bonus = request.POST.get('bonus', 0.0)  # Récupérer le bonus
        reference = request.POST['reference']  # Récupérer la référence

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'transactions/edit-expense.html', context)

        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'transactions/edit-expense.html', context)

        expense.owner = request.user
        expense.amount = amount
        expense.date = date
        expense.category = category
        expense.description = description
        expense.bonus = bonus  # Mettre à jour le bonus
        expense.reference = reference  # Mettre à jour la référence

        expense.save()
        messages.success(request, 'Transaction mise à jour succès')

        return redirect('transactions')

def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Transaction est supprimer')
    return redirect('transactions')

def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    expenses = Expense.objects.filter(owner=request.user,
                                       date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}

    def get_category(expense):
        return expense.category

    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filter_by_category = expenses.filter(category=category)

        for item in filter_by_category:
            amount += item.amount
        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)
    return JsonResponse({'expense_category_data': finalrep}, safe=False)

def stats_view(request):
    return render(request, 'transactions/stats.html')

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + \
        str(datetime.datetime.now()) + '.csv'

    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])

    expenses = Expense.objects.filter(owner=request.user)

    for expense in expenses:
        writer.writerow([expense.amount, expense.description,
                         expense.category, expense.date])
    return response

def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + \
        str(datetime.datetime.now()) + '.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Amount', 'Description', 'Category', 'Date']
    
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
        font_style = xlwt.XFStyle()

    rows = Expense.objects.filter(owner=request.user).values_list(
        'amount', 'description', 'category', 'date')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)
    
    return response

def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; attachment; filename=Expenses' + \
        str(datetime.datetime.now()) + '.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    expenses = Expense.objects.filter(owner=request.user)

    total_sum = expenses.aggregate(Sum('amount'))

    html_string = render_to_string(
        'transactions/pdf-output.html', {'expenses': expenses, 'total': total_sum})
    html = HTML(string=html_string)
   
    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')
        response.write(output.read())  

    return response


def analyze_expenses(request):
    expenses = Expense.objects.filter(owner=request.user)

    # Filtrage par date
    if 'start_date' in request.GET and 'end_date' in request.GET:
        start_date = request.GET['start_date']
        end_date = request.GET['end_date']
        expenses = expenses.filter(date__range=[start_date, end_date])

    # Filtrage par catégorie
    if 'category' in request.GET and request.GET['category']:
        category = request.GET['category']
        expenses = expenses.filter(category=category)

    # Filtrage par description
    if 'description' in request.GET and request.GET['description']:
        description = request.GET['description']
        expenses = expenses.filter(description__icontains=description)

    # Calculer la somme du montant et du bonus pour les filtres appliqués
    total_amount = expenses.aggregate(total_amount=Sum('amount'))['total_amount'] or 0.0
    total_bonus = expenses.aggregate(total_bonus=Sum('bonus'))['total_bonus'] or 0.0

    context = {
        'expenses': expenses,
        'categories': Expense.objects.values_list('category', flat=True).distinct(),
        'total_amount': total_amount,
        'total_bonus': total_bonus,
    }
    return render(request, 'transactions/analyze_expenses.html', context)








