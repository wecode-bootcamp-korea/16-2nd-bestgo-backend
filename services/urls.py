from django.urls  import path,include
from services     import views

urlpatterns = [
     path('/categories', views.CategoryView.as_view()),
     path('/services', views.ServiceListView.as_view()),
     path('/regions', views.RegionListView.as_view()),
     path('/details', views.ServiceDetailView.as_view()),
     path('/questions', views.QuestionView.as_view())
]
