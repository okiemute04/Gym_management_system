from datetime import date
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Invoice, InvoiceLine, Membership, Checkin
from .serializers import InvoiceSerializer, MembershipSerializer, CheckinSerializer, CheckinCreateSerializer, \
    InvoiceLineSerializer



class InvoiceViewSet(viewsets.ModelViewSet):
    STATUS_CHOICES = (
        ('outstanding', 'Outstanding'),
        ('paid', 'Paid'),
        ('void', 'Void'),
    )

    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    @action(detail=True, methods=['POST'])
    def add_line(self, request, pk=None):
        invoice = self.get_object()
        serializer = InvoiceLineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(invoice=invoice)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer

    def get_queryset(self):
        queryset = Membership.objects.all()
        start_date = self.request.query_params.get('start_date', None)
        if start_date is not None:
            queryset = queryset.filter(start_date__gte=start_date)
        return queryset


class CheckinViewSet(viewsets.ModelViewSet):
    queryset = Checkin.objects.all()
    serializer_class = CheckinSerializer

    INVOICE_LINE_DESCRIPTION = 'Monthly Membership Fee'

    STATUS_CHOICES = (
        ('outstanding', 'Outstanding'),
        ('paid', 'Paid'),
        ('void', 'Void'),
    )

    def get_serializer_class(self):
        if self.action == 'create':
            return CheckinCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        membership = serializer.validated_data['membership']
        membership.credits -= 1
        membership.save()
        super().perform_create(serializer)
        invoice, created = Invoice.objects.get_or_create(date=date.today())
        if created:
            invoice.status = self.STATUS_CHOICES[0][0]
            invoice.save()
        invoice_line = InvoiceLine(invoice=invoice, description=self.INVOICE_LINE_DESCRIPTION)
        invoice_line.save()
