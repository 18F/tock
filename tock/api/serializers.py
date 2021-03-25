from hours.models import Timecard
from rest_framework import serializers


class TimecardSummarySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    reporting_start_date = serializers.DateField(
        source='reporting_period.start_date'
    )
    reporting_end_date = serializers.DateField(
        source='reporting_period.end_date'
    )
    unit = serializers.StringRelatedField()
    organization = serializers.StringRelatedField()

    class Meta:
        model = Timecard
        exclude = ['time_spent', 'reporting_period', 'created', 'modified']
