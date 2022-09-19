from rest_framework import serializers
from .models import LoanList, RepaymentSchedule

class LoanListSerialzier(serializers.ModelSerializer):
    class Meta:
        model = LoanList
        fields = '__all__'


class RepaymentScheduleSerialzier(serializers.ModelSerializer):
    class Meta:
        model = RepaymentSchedule
        fields = '__all__'