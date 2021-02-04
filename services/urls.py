from django.urls  import path,include
from services     import views

urlpatterns = [
     path('/categories', views.CategoryView.as_view()),
     path('/services', views.ServiceListView.as_view()),
     path('/regions', views.RegionListView.as_view()),
     path('/details', views.ServiceDetailView.as_view()),
     path('/questions', views.QuestionView.as_view()),
     path('/requests', views.RequestView.as_view()),
     path('/matchMasters', views.RequestDistributionView.as_view()),
     path('/receivedRequest', views.ReceivedRequestListView.as_view()),
     path('/requestDetail', views.ReceivedRequestDetailView.as_view()),
     path('/createQuotation', views.QuotationView.as_view()),
     path('/quotationList', views.QuotationListView.as_view()),
]
