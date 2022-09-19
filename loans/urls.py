from django.urls import path
from . import views

urlpatterns = [
  path("", views.get_listings_or_add_new_loan, name="retrieve all listings or add new loan"),
  path("<int:pk>/", views.get_modifiy_delete_loan, name="retrieve, modifity or delete listing and associated repayment data"),
  path("advanced-search/", views.filter_loans, name="filter loans based on user defind parameters"),
  path("get-loan-data/<int:pk>/", views.get_loan_data, name="retrieve loan information for editting"),
]