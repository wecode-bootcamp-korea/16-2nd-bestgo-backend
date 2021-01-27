from django.urls  import path,include
from services     import views

urlpatterns = [
     path('/categories', views.CategoryView.as_view()),
     path('/services', views.ServiceListView.as_view()),
]
