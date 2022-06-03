from django.urls import path
from . import views

#configurando la primera url con mi vista index
#configurando la primera url con mi vista signup
app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
]