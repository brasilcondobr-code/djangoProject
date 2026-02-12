from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Sistema Django Rodando com Sucesso! 🚀</h1><p>Ambiente Docker configurado corretamente.</p>")