from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Invoice, InvoiceLine, Membership, Checkin
from datetime import datetime





class ModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.invoice = Invoice.objects.create(user=self.user, date='2022-01-01', status='outstanding', description='Test invoice', amount=100.00)
        self.invoice_line = InvoiceLine.objects.create(invoice=self.invoice, description='Test invoice line', amount=50.00)
        self.membership = Membership.objects.create(user=self.user, state='active', credits=10, start_date='2022-01-01', end_date='2023-01-01')
        self.checkin = Checkin.objects.create(user=self.user, membership=self.membership)

    def test_invoice(self):
        self.assertEqual(str(self.invoice), 'Invoice #1')

    def test_invoice_line(self):
        self.assertEqual(str(self.invoice_line), 'Test invoice line')

    def test_membership(self):
        self.assertEqual(str(self.membership), 'Membership #1')

    def test_checkin(self):
        self.assertEqual(str(self.checkin), f'Checkin for {self.user.username} on {self.checkin.timestamp.date()}')


class InvoiceViewSetTests(APITestCase):

    def test_add_invoice_line(self):
        invoice = Invoice.objects.create(date='2022-01-01', status='outstanding', description='Test invoice',
                                         amount=100.00)
        url = reverse('invoice-add-line', args=[invoice.pk])
        data = {'description': 'Test invoice line', 'amount': 50.00}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(InvoiceLine.objects.count(), 1)
        self.assertEqual(InvoiceLine.objects.get().description, 'Test invoice line')

        url = reverse('invoice-detail', args=[invoice.pk])
        data = {'status': 'paid'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, 'paid')

    def test_add_multiple_invoice_lines(self):
        invoice = Invoice.objects.create(date='2022-01-01', status='outstanding', description='Test invoice',
                                         amount=100.00)
        url = reverse('invoice-add-line', args=[invoice.pk])
        data1 = {'description': 'Test invoice line 1', 'amount': 50.00}
        data2 = {'description': 'Test invoice line 2', 'amount': 25.00}
        response1 = self.client.post(url, data1, format='json')
        response2 = self.client.post(url, data2, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(InvoiceLine.objects.count(), 2)
        self.assertEqual(InvoiceLine.objects.all()[0].description, 'Test invoice line 1')
        self.assertEqual(InvoiceLine.objects.all()[1].description, 'Test invoice line 2')

    def test_retrieve_invoice(self):
        invoice = Invoice.objects.create(date='2022-01-01', status='outstanding', description='Test invoice',
                                         amount=100.00)
        url = reverse('invoice-detail', args=[invoice.pk])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], invoice.pk)
        self.assertEqual(response.data['date'], '2022-01-01')
        self.assertEqual(response.data['status'], 'outstanding')
        self.assertEqual(response.data['description'], 'Test invoice')
        self.assertEqual(response.data['amount'], '100.00')


    def test_list_invoices(self):
        invoice1 = Invoice.objects.create(date='2022-01-01', status='outstanding', description='Test invoice 1',
                                          amount=100.00)
        invoice2 = Invoice.objects.create(date='2022-02-01', status='paid', description='Test invoice 2',
                                          amount=75.00)
        url = reverse('invoice-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['id'], invoice1.pk)
        self.assertEqual(response.data[1]['id'], invoice2.pk)




    def test_update_invoice(self):
        invoice = Invoice.objects.create(date='2022-01-01', status='outstanding', description='Test invoice',
                                         amount=100.00)
        url = reverse('invoice-detail', args=[invoice.pk])
        data = {'status': 'paid', 'description': 'Updated invoice'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, 'paid')
        self.assertEqual(invoice.description, 'Updated invoice')

    def test_delete_invoice(self):
        invoice = Invoice.objects.create(date='2022-01-01', status='outstanding', description='Test invoice',
                                         amount=100.00)
        url = reverse('invoice-detail', args=[invoice.pk])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Invoice.objects.filter(pk=invoice.pk).exists())

    def test_add_invoice_line_with_invalid_data(self):
        invoice = Invoice.objects.create(date='2022-01-01', status='outstanding', description='Test invoice',
                                         amount=100.00)
        url = reverse('invoice-add-line', args=[invoice.pk])
        data = {'description': '', 'amount': -50.00}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(InvoiceLine.objects.filter(invoice=invoice).exists())

    def test_add_invoice_line_to_nonexistent_invoice(self):
        url = reverse('invoice-add-line', args=[999])
        data = {'description': 'Test invoice line', 'amount': 50.00}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(InvoiceLine.objects.exists())

    def test_retrieve_nonexistent_invoice(self):
        url = reverse('invoice-detail', args=[999])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



    def test_list_invoices_with_pagination(self):
        for i in range(10):
            date_str = f'2022-01-{10-i:02d}'
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                self.fail(f"Invalid date: {date_str}")
            Invoice.objects.create(date=date, status='outstanding', description=f'Test invoice {i}',
                                   amount=(i+1)*10.00)
        url = reverse('invoice-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)
        self.assertEqual(response.data[0]['description'], 'Test invoice 0')
        self.assertEqual(response.data[9]['description'], 'Test invoice 9')



class MembershipViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.membership1 = Membership.objects.create(user=self.user, state='active', credits=10,
                                                     start_date='2022-01-01', end_date='2023-01-01')
        self.membership2 = Membership.objects.create(user=self.user, state='canceled', credits=5,
                                                     start_date='2023-01-01', end_date='2024-01-01')

    def test_get_memberships(self):
        url = reverse('membership-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_membership_detail(self):
        url = reverse('membership-detail', args=[self.membership1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], 'active')

    def test_create_membership(self):
        url = reverse('membership-list')
        data = {
            'user': self.user.id,
            'state': 'active',
            'credits': 15,
            'start_date': '2022-04-01',
            'end_date': '2023-04-01'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Membership.objects.count(), 3)


    def test_update_membership(self):
        url = reverse('membership-detail', args=[self.membership2.id])
        data = {
            'state': 'active',
            'credits': 10,
            'start_date': '2022-02-01',
            'end_date': '2023-02-01'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('state', response.data)

    def test_delete_membership(self):
        url = reverse('membership-detail', args=[self.membership2.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Membership.objects.count(), 1)

    def test_filter_memberships_by_user(self):
        url = reverse('membership-list')
        response = self.client.get(url, {'user': self.user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_memberships_by_state(self):
        url = reverse('membership-list')
        response = self.client.get(url, {'state': 'active'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        active_memberships = [m for m in response.data if m['state'] == 'active']
        self.assertEqual(len(active_memberships), 1)
        active_membership = active_memberships[0]
        self.assertEqual(active_membership['user'], self.user.id)
        self.assertEqual(active_membership['state'], 'active')
        self.assertEqual(active_membership['credits'], 10)


    def test_filter_memberships_by_start_date(self):
        url = reverse('membership-list')
        response = self.client.get(url, {'start_date': '2023-01-01'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        expected_membership = Membership.objects.get(state='canceled')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], expected_membership.id)
        self.assertEqual(response.data[0]['user'], expected_membership.user.id)
        self.assertEqual(response.data[0]['state'], expected_membership.state)
        self.assertEqual(response.data[0]['credits'], expected_membership.credits)
        self.assertEqual(response.data[0]['start_date'], str(expected_membership.start_date))
        self.assertEqual(response.data[0]['end_date'], str(expected_membership.end_date))

    def test_filter_memberships_by_end_date(self):
        url = reverse('membership-list')
        response = self.client.get(url, {'end_date': '2023-01-01'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['user'], self.user.id)
        self.assertEqual(response.data[0]['state'], 'active')
        self.assertEqual(response.data[0]['credits'], 10)


class CheckinViewSetTests(APITestCase):

    def test_create_checkin_with_valid_membership(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        membership = Membership.objects.create(user=user, state='active', credits=10, start_date='2022-01-01',
                                               end_date='2024-01-01')
        url = reverse('checkin-list')
        data = {'membership': membership.pk, 'user': user.pk}
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Checkin.objects.count(), 1)
        checkin = Checkin.objects.first()
        self.assertEqual(checkin.membership, membership)
        self.assertEqual(checkin.user, user)

    def test_create_checkin_with_canceled_membership(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        membership = Membership.objects.create(user=user, state='canceled', credits=10, start_date='2022-01-01',
                                               end_date='2023-01-01')
        url = reverse('checkin-list')
        data = {'membership': membership.pk}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_checkin_with_no_credits_membership(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        membership = Membership.objects.create(user=user, state='active', credits=0, start_date='2022-01-01',
                                               end_date='2023-01-01')
        url = reverse('checkin-list')
        data = {'membership': membership.pk}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_checkin_with_expired_membership(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        membership = Membership.objects.create(user=user, state='active', credits=10, start_date='2022-01-01',
                                               end_date='2022-02-01')
        url = reverse('checkin-list')
        data = {'membership': membership.pk}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)




    def test_create_checkin_with_invalid_membership(self):
        url = reverse('checkin-list')
        data = {'membership': 999}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_checkin_with_different_user(self):
        user1 = User.objects.create_user(username='testuser1', password='testpass')
        user2 = User.objects.create_user(username='testuser2', password='testpass')
        membership = Membership.objects.create(user=user1, state='active', credits=10, start_date='2022-01-01',
                                               end_date='2024-01-01')
        url = reverse('checkin-list')
        data = {'membership': membership.pk, 'user': user2.pk}
        self.client.force_authenticate(user=user1)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_checkin_with_duplicate_membership(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        membership = Membership.objects.create(user=user, state='active', credits=10, start_date='2022-01-01',
                                               end_date='2024-01-01')
        Checkin.objects.create(membership=membership, user=user)
        url = reverse('checkin-list')
        data = {'membership': membership.pk, 'user': user.pk}
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_checkin_with_nonexistent_membership(self):
        url = reverse('checkin-list')
        data = {'membership': 999}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_checkin_with_invalid_user(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        membership = Membership.objects.create(user=user, state='active', credits=10, start_date='2022-01-01',
                                               end_date='2024-01-01')
        url = reverse('checkin-list')
        data = {'membership': membership.pk, 'user': 999}
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_checkin_with_membership_not_yet_started(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        membership = Membership.objects.create(user=user, state='active', credits=10, start_date='2023-05-01',
                                               end_date='2024-05-01')
        url = reverse('checkin-list')
        data = {'membership': membership.pk}
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)




    def test_create_checkin_with_exceeded_credit_limit(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        membership = Membership.objects.create(user=user, state='active', credits=2, start_date='2022-01-01',
                                               end_date='2023-01-01')
        Checkin.objects.create(membership=membership, user=user)
        Checkin.objects.create(membership=membership, user=user)
        url = reverse('checkin-list')
        data = {'membership': membership.pk, 'user': user.pk}
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


