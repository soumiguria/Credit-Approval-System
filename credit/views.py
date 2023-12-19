# testproject/views.py

# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from .models import Customer, Loan
# from .serializers import CustomerSerializer, LoanSerializer
# import datetime

# views.py

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .serializers import RegisterSerializer, CheckEligibilityRequestSerializer, CheckEligibilityResponseSerializer, CreateLoanSerializer, CreateLoanResponseSerializer, ViewLoanResponseSerializer, ViewLoanListSerializer

def calculate_corrected_interest_rate(credit_rating, interest_rate):
    if credit_rating > 50:
        return interest_rate  # No correction needed

    # Calculate corrected interest rate based on credit rating slabs
    if 30 < credit_rating <= 50:
        return max(interest_rate, 12.0)
    elif 10 < credit_rating <= 30:
        return max(interest_rate, 16.0)
    else:
        # Do not approve any loans for credit_rating <= 10
        return None  # or return an appropriate value

# Example usage:
credit_rating = 40  # Replace with the actual credit rating value
interest_rate = 8.0  # Replace with the actual interest rate value
corrected_interest_rate = calculate_corrected_interest_rate(credit_rating, interest_rate)

print(corrected_interest_rate)

def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    # Convert annual interest rate to monthly and percentage to decimal
    r = (interest_rate / 12) * 0.01
    # Calculate number of monthly installments
    n = tenure
    # Calculate monthly installment using the formula
    emi = loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    return emi

# Example usage:
loan_amount = 10000  # Replace with the actual loan amount
interest_rate = 12.0  # Replace with the actual interest rate
tenure = 12  # Replace with the actual tenure in months

monthly_installment = calculate_monthly_installment(loan_amount, interest_rate, tenure)

print(monthly_installment)


@api_view(['POST'])
def register_customer(request):
        # Validate and process the request data
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        # Calculate the approved limit based on the provided formula
        monthly_salary = serializer.validated_data['monthly_income']
        approved_limit = round(36 * monthly_salary, -5)

        # Save the customer to the database
        customer = serializer.save(approved_limit=approved_limit)

        # Prepare the response data
        response_data = {
            'customer_id': customer.id,
            'name': f"{customer.first_name} {customer.last_name}",
            'age': customer.age,
            'monthly_income': customer.monthly_income,
            'approved_limit': customer.approved_limit,
            'phone_number': customer.phone_number,
        }

        # Return success response
        return Response(response_data, status=status.HTTP_201_CREATED)

    # Return error response for invalid data
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
def check_loan_eligibility(request):
     # Validate and process the request data
    serializer = CheckEligibilityRequestSerializer(data=request.data)
    if serializer.is_valid():
        customer_id = serializer.validated_data['customer_id']
        loan_amount = serializer.validated_data['loan_amount']
        interest_rate = serializer.validated_data['interest_rate']
        tenure = serializer.validated_data['tenure']

        # Fetch customer and loan data from the database
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

        loans = Loan.objects.filter(customer=customer)

        # Perform credit score calculations and loan eligibility checks
        # Implement your logic here based on the provided criteria

        # Prepare the response data
        response_data = {
            'customer_id': customer.id,
            'approval': True,  # Set this based on your eligibility logic
            'interest_rate': interest_rate,  # Modify based on corrected rate if needed
            'corrected_interest_rate': corrected_interest_rate,  # Your corrected interest rate logic
            'tenure': tenure,
            'monthly_installment': monthly_installment,  # Calculate based on your logic
        }

        # Return the response
        return Response(response_data, status=status.HTTP_200_OK)

    # Return error response for invalid data
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_loan(request):
    # Validate and process the request data
    serializer = CreateLoanSerializer(data=request.data)
    if serializer.is_valid():
        customer_id = serializer.validated_data['customer_id']
        loan_amount = serializer.validated_data['loan_amount']
        interest_rate = serializer.validated_data['interest_rate']
        tenure = serializer.validated_data['tenure']

        # Fetch customer from the database
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check eligibility and process the loan
        # Implement your logic here based on the provided criteria

        # For demonstration purposes, let's assume the loan is approved
        loan_approved = True
        loan_id = 123  # Replace with the actual ID if approved
        message = "Loan approved successfully"
        monthly_installment = 1000.0  # Replace with your calculated value

        # Create the Loan record if approved
        if loan_approved:
            Loan.objects.create(customer=customer, loan_amount=loan_amount,
                                interest_rate=interest_rate, tenure=tenure)

        # Prepare the response data
        response_data = {
            'loan_id': loan_id if loan_approved else None,
            'customer_id': customer.id,
            'loan_approved': loan_approved,
            'message': message,
            'monthly_installment': monthly_installment if loan_approved else None,
        }

        # Return the response
        return Response(response_data, status=status.HTTP_200_OK)

    # Return error response for invalid data
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def view_loan(request, loan_id):
    # Fetch loan from the database
    try:
        loan = Loan.objects.get(id=loan_id)
    except Loan.DoesNotExist:
        return Response({'error': 'Loan not found'}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the loan and customer data
    serializer = ViewLoanListSerializer(loan)

    # Return the response
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def view_loans_by_customer(request, customer_id):
    # Fetch all loans for the given customer from the database
    loans = Loan.objects.filter(customer_id=customer_id)

    # Serialize the list of loans
    serializer = ViewLoanListSerializer(loans, many=True)

    # Return the response
    return Response(serializer.data, status=status.HTTP_200_OK)
