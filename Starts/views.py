from django.shortcuts import render

# Create your views here.
def index(request):
	return render(request, 'Starts/index.html')

def analysis(request):
	return render(request,'Starts/analysis.html')

def products(request):
	return render(request, 'Starts/products.html')

def contacts(request):
	return render(request,'Starts/contacts.html')
