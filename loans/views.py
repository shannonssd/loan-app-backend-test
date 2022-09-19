from .models import RepaymentSchedule, LoanList
from django.db import transaction
from datetime import datetime
from dateutil import relativedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import LoanListSerialzier, RepaymentScheduleSerialzier

#### 1. principal spelling
#### 2. interest rate constraint
#### 3. adding date / month to loan list db table
#### 4. Commnets




# GET - Retrieve all listings on page load 
# POST - Add new loan
@api_view(['GET', 'POST'])
def get_listings_or_add_new_loan(request):
    try:    
        if request.method == 'GET':
            loan_list = LoanList.objects.all()
            loan_list_serializer = LoanListSerialzier(loan_list, many=True).data
            return Response(loan_list_serializer)

        elif request.method == 'POST':
            # Use a database transaction as data is being saved across two tables
            with transaction.atomic():
                print('POST working')
                loan_amount_int = int(request.data['loan_amount'])
                loan_term_int = int(request.data['loan_term'])
                interest_rate_int = float(request.data['interest_rate'])
                loan_month = request.data['loan_month']
                loan_year = str(request.data['loan_year'])
                new_loan = LoanList(
                    loan_amount = loan_amount_int, 
                    loan_term = loan_term_int, 
                    interest_rate = interest_rate_int, 
                    loan_year = loan_year, 
                    loan_month = loan_month,
                    ) 
                new_loan.save()
                return calculate_repayment(loan_amount_int, loan_term_int, interest_rate_int, loan_month, loan_year, new_loan)
                
    except Exception as err:
        print(str(err))
        return Response(str(err))
    

# GET - Retrieve single loan and repayment details from db
# DELETE - Delete loan and repayment details from db
# PUT - Update loan and repayment details from db
@api_view(['GET', 'DELETE', 'PUT'])
def get_modifiy_delete_loan(request, pk):
    try:
        if request.method == 'GET':
            print(pk)
            loan_details = LoanList.objects.get(id=pk)
            loan_serializer =  LoanListSerialzier(loan_details).data
            repayment_details = RepaymentSchedule.objects.filter(loan_id_id__id = pk)
            repayments_serializer = RepaymentScheduleSerialzier(repayment_details , many=True).data
            obj = {
            'loan': loan_serializer,
            'repayment list': repayments_serializer
            }
            return Response(obj)

        elif request.method == 'DELETE':
            repayment_list = RepaymentSchedule.objects.filter(loan_id_id__id = pk)
            repayment_list.delete()
            loan_listing = LoanList.objects.get(id=pk)
            loan_listing.delete()
            loan_list = LoanList.objects.all()
            loan_list_serializer = LoanListSerialzier(loan_list, many=True).data
            return Response(loan_list_serializer)

        elif request.method == 'PUT':
            # Use a database transaction as data is being saved across two tables
            with transaction.atomic():
                # Remove previous repayment entries from db
                repayment_list = RepaymentSchedule.objects.filter(loan_id_id__id = pk)
                repayment_list.delete()
                # Retrieve and update loan info
                loan_amount_int = int(request.data['loan_amount'])
                loan_term_int = int(request.data['loan_term'])
                interest_rate_int = float(request.data['interest_rate'])
                loan_month = request.data['loan_month']
                loan_year = str(request.data['loan_year'])
                LoanList.objects.filter(id=pk).update(
                    loan_amount = loan_amount_int, 
                    loan_term = loan_term_int, 
                    interest_rate = interest_rate_int, 
                    loan_year = loan_year, 
                    loan_month = loan_month,
                    )
                loan_details = LoanList.objects.get(id=pk)
                return calculate_repayment(loan_amount_int, loan_term_int, interest_rate_int, loan_month, loan_year, loan_details)

    except Exception as err:
        print(str(err))
        return Response(str(err))

# Filter and return loan listings based on user parameters
@api_view(['GET'])
def filter_loans(request):
    print('working', request.GET)
    try:
        if request.GET['loan_amount_lower'] == 'null':
            loan_amount_lower = 1000 
        else:
            loan_amount_lower = int(request.GET['loan_amount_lower'])

        if request.GET['loan_amount_upper'] == 'null':
            loan_amount_upper = 100000000 
        else:
            loan_amount_upper = int(request.GET['loan_amount_upper'])

        if request.GET['loan_term_lower'] == 'null':
            loan_term_lower = 1 
        else:
            loan_term_lower = int(request.GET['loan_term_lower'])

        if request.GET['loan_term_upper'] == 'null':
            loan_term_upper = 50 
        else:
            loan_term_upper = int(request.GET['loan_term_upper'])

        if request.GET['interest_rate_lower'] == 'null':
            interest_rate_lower = 1.0
        else:
            interest_rate_lower = float(request.GET['interest_rate_lower'])

        if request.GET['interest_rate_upper'] == 'null':
            interest_rate_upper = 36.0
        else:
            interest_rate_upper = float(request.GET['interest_rate_upper'])

        filtered_list = LoanList.objects.filter(
            loan_amount__gte=loan_amount_lower, 
            loan_amount__lte=loan_amount_upper, 
            loan_term__gte=loan_term_lower, 
            loan_term__lte=loan_term_upper, 
            interest_rate__gte=interest_rate_lower, 
            interest_rate__lte=interest_rate_upper, 
            )

        filtered_loans_serializer =  LoanListSerialzier(filtered_list, many=True).data
        return Response(filtered_loans_serializer)

    except Exception as err:
        print(str(err))
        return Response(str(err))

# Retrieve loan information for editting
@api_view(['GET'])
def get_loan_data(request, pk):
    loan_details = LoanList.objects.get(id=pk)
    loan_serializer =  LoanListSerialzier(loan_details).data
    return Response({"loanObject": loan_serializer })

# Helper function to calculate and store repayment schedule in db
def calculate_repayment(loan_amount, loan_term, interest_rate_percentage, loan_month, loan_year, loan):
    print('calc started')
    print(loan_month, loan_year)
    interest_rate = interest_rate_percentage / 100
    pmt = loan_amount * (interest_rate/12) / (1 - ((1 + (interest_rate/12)) ** (-12 * loan_term)))
    no_of_months = loan_term * 12
    balance = loan_amount

    repayment_list = []
    for x in range(1, no_of_months + 1):
        monthly_interest = (interest_rate / 12) * balance
        principal = pmt - monthly_interest
        balance = balance - principal

        repayment_list.append(RepaymentSchedule(
            loan_id = loan,
            payment_no = x,
            date =  datetime(loan_year, int(loan_month), 1) + relativedelta.relativedelta(months=x),
            payment_amount = pmt,
            principal = principal,
            interest = monthly_interest,
            balance = balance
        ))

    RepaymentSchedule.objects.bulk_create(repayment_list)
    # added_repayments = RepaymentSchedule.objects.filter(loan_id_id = loan)
    # repayments_serializer = RepaymentScheduleSerialzier(added_repayments, many=True).data
    loan_serializer =  LoanListSerialzier(loan).data
    print(loan_serializer)
    pk = loan_serializer['id']
    print(pk)
    # obj = {
    #     'loan': loan_serializer,
    #     'repayment list': repayments_serializer
    # }
    return Response(pk)

