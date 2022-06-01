from django.urls import path
from . import views

#configurando la primera url con mi vista index
app_name = 'core'
urlpatterns = [
    path('', views.index, name='index')
]