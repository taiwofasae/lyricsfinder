from django.shortcuts import render, redirect
from .forms import OrderForm
from .models import Orders

# Create your views here.

def orderFormView(request):
    form = OrderForm()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('show_url')
    
    template_name = 'ofv.html'
    context = {'form': form}
    return render(request, template_name, context)

def showView(request):
    obj = Orders.objects.all()
    template_name = 'sv.html'
    context = {'obj': obj}
    return render(request, template_name, context)

def updateView(request, f_oid):
    obj = Orders.objects.get(oid=f_oid)
    form = OrderForm(instance=obj)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('show_url')
    
    template_name = 'order.html'
    context = {'form': form}
    return render(request, template_name, context)

def deleteView(request, f_oid):
    obj = Orders.objects.get(oid=f_oid)
    if request.method == 'POST':
        obj.delete()
        return redirect('show_url')
    template_name = 'confirmation.html'
    context = {'obj': obj}
    return render(request, template_name, context)