from django.shortcuts import render, redirect

from django.urls import reverse

from django.views import View

from .models import FoodDonation, FoodClaim

from django.conf import settings

from django.db.models import Q

from django.contrib.auth.decorators import login_required

from django.utils.decorators import method_decorator

from accounts.custom_permissions import allowed_roles

from accounts.models import Profile

from django.utils import timezone

import razorpay

from django.conf import settings

from django.views.decorators.csrf import csrf_exempt


class DonationListView(View):

    template = 'donations/list.html'

    page = 'Available Food'

    def get(self, request, *args, **kwargs):

        donations = FoodDonation.objects.filter(
        
            active_status=True,
        
            status='Available',
        
            expiry_time__gt=timezone.now()
        )

        query = request.GET.get('query')

        if query:

            donations = donations.filter(

                Q(food_name__icontains=query) |

                Q(description__icontains=query) |

                Q(location__icontains=query)
            )


        data = {'page': self.page, 'donations': donations, 'query': query}

        return render(request, self.template, context=data)

@method_decorator(allowed_roles(['Donor']), name='dispatch')
class AddDonationView(View):

    template = 'donations/add-donation.html'

    page = 'Post Food Donation'

    def get(self, request, *args, **kwargs):

        data = {'page': self.page}

        return render(request, self.template, context=data)

    def post(self, request, *args, **kwargs):

        food_name = request.POST.get('food_name')

        description = request.POST.get('description')

        quantity = request.POST.get('quantity')

        price = request.POST.get('price')

        location = request.POST.get('location')

        expiry_time = request.POST.get('expiry_time')

        photo = request.FILES.get('photo')

        FoodDonation.objects.create(

            donor=request.user,

            food_name=food_name,

            description=description,

            quantity=quantity,

            quantity_remaining=quantity,

            price=price,

            location=location,

            expiry_time=expiry_time,

            photo=photo,
        )

        return redirect('donation-list')


class DonationDetailView(View):

    template = 'donations/detail.html'

    def get(self, request, *args, **kwargs):
    
        uuid = kwargs.get('uuid')
    
        donation = FoodDonation.objects.get(uuid=uuid)
    
        data = {'donation': donation}
    
        return render(request, self.template, context=data)


@method_decorator(allowed_roles(['User', 'NGO']), name='dispatch')
class ClaimFoodView(View):

    def post(self, request, *args, **kwargs):

        uuid = kwargs.get('uuid')

        donation = FoodDonation.objects.get(uuid=uuid)

        if donation.donor == request.user:
        
            return redirect('donation-list')

        quantity_claimed = int(request.POST.get('quantity_claimed'))

        # NGO gets free — save directly
        if request.user.role == 'NGO' and request.user.is_verified:

            FoodClaim.objects.create(
        
                donation=donation,
        
                recipient=request.user,
        
                quantity_claimed=quantity_claimed,
        
                amount_paid=0
            )

            donation.quantity_remaining -= quantity_claimed

            if donation.quantity_remaining <= 0:
        
                donation.status = 'Completed'

            donation.save()

            return redirect('my-claims')

        # User → go to Razorpay payment page
        return redirect(f'/donation/{uuid}/payment/?quantity={quantity_claimed}')

@method_decorator(allowed_roles(['Donor']), name='dispatch')
class EditDonationView(View):

    template = 'donations/edit-donation.html'

    page = 'Edit Donation'

    def get(self, request, *args, **kwargs):

        uuid = kwargs.get('uuid')

        donation = FoodDonation.objects.get(uuid=uuid)

        if donation.donor != request.user:
            return redirect('donation-list')

        data = {'page': self.page, 'donation': donation}

        return render(request, self.template, context=data)

    def post(self, request, *args, **kwargs):

        uuid = kwargs.get('uuid')

        donation = FoodDonation.objects.get(uuid=uuid)

        if donation.donor != request.user:
            return redirect('donation-list')

        donation.food_name = request.POST.get('food_name')

        donation.description = request.POST.get('description')

        donation.price = request.POST.get('price')

        donation.location = request.POST.get('location')

        donation.expiry_time = request.POST.get('expiry_time')

        donation.save()

        return redirect('donation-detail', uuid=donation.uuid)

@method_decorator(allowed_roles(['Donor']), name='dispatch') #What name='dispatch' means
                                                            #dispatch is the first method Django calls on any view — before get() or post(). So decorating dispatch means the check runs for ALL requests (GET and POST both), not just one.
                                                            #Request comes in
                                                            # → dispatch() runs first  ← decorator checks role HERE
                                                            #  → if allowed → get() or post() runs
                                                            # → if not allowed → redirect to login
class DeleteDonationView(View):

    def get(self, request, *args, **kwargs):

        uuid = kwargs.get('uuid')

        donation = FoodDonation.objects.get(uuid=uuid)

        if donation.donor != request.user:
            return redirect('donation-list')

        # Soft delete — same as Cake Tales!

        donation.active_status = False

        donation.save()

        return redirect('donation-list')
    

@method_decorator(allowed_roles(['Admin']), name='dispatch')

class AdminDashboardView(View):

    template = 'donations/admin-dashboard.html'

    def get(self, request, *args, **kwargs):

        donations = FoodDonation.objects.filter(active_status=True).order_by('-created_at') # the - means newest first.

        total_donations = donations.count()

        total_users = Profile.objects.filter(role='User').count()

        total_donors = Profile.objects.filter(role='Donor').count()

        total_ngos = Profile.objects.filter(role='NGO').count()

        pending_ngos = Profile.objects.filter(role='NGO', is_verified=False).count()

        data = {

            'donations': donations,

            'total_donations': total_donations,

            'total_users': total_users,

            'total_donors': total_donors,

            'total_ngos': total_ngos,

            'pending_ngos': pending_ngos,

        }

        return render(request, self.template, context=data)


@method_decorator(allowed_roles(['Admin']), name='dispatch')

class AdminUsersView(View):

    template = 'donations/admin-users.html'

    def get(self, request, *args, **kwargs):

        users = Profile.objects.exclude(role='Admin').order_by('role', 'username')

        data = {'users': users}

        return render(request, self.template, context=data)


@method_decorator(allowed_roles(['Admin']), name='dispatch')

class VerifyNGOView(View):

    def get(self, request, *args, **kwargs):

        ngo_id = kwargs.get('id')

        ngo = Profile.objects.get(id=ngo_id)

        ngo.is_verified = True

        ngo.save()

        return redirect('admin-users')
    
@method_decorator(allowed_roles(['Donor']), name='dispatch')
class MyDonationsView(View):

    template = 'donations/my-donations.html'

    def get(self, request, *args, **kwargs):
        
        donations = FoodDonation.objects.filter(
        
            donor=request.user,
        
            active_status=True
        
        ).order_by('-created_at')

        data = {'donations': donations}
        
        return render(request, self.template, context=data)
    
@method_decorator(allowed_roles(['User', 'NGO']), name='dispatch')
class MyClaimsView(View):

    template = 'donations/my-claims.html'

    def get(self, request, *args, **kwargs):

        claims = FoodClaim.objects.filter(

            recipient=request.user,

            active_status=True

        ).order_by('-claimed_at')

        data = {'claims': claims}

        return render(request, self.template, context=data)
    
@method_decorator(allowed_roles(['User']), name='dispatch')
class PaymentView(View):

    template = 'donations/payment.html'

    def get(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        quantity = request.GET.get('quantity', 1)
        donation = FoodDonation.objects.get(uuid=uuid)

        amount = int(donation.price * int(quantity) * 100)  # Razorpay needs paise

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        razorpay_order = client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': 1
        })

        success_path = reverse('payment-success', kwargs={'uuid': uuid}) + f'?quantity={quantity}'
        absolute_url = request.build_absolute_uri(success_path)
        host = request.get_host()
        callback_url = absolute_url if ('localhost' not in host and '127.0.0.1' not in host) else ''

        data = {
            'donation': donation,
            'quantity': quantity,
            'amount': amount,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'callback_url': callback_url,
        }
        return render(request, self.template, context=data)


@method_decorator(csrf_exempt, name='dispatch')
class PaymentSuccessView(View):

    def post(self, request, *args, **kwargs):
     
        uuid = kwargs.get('uuid')
     
        quantity = int(request.POST.get('quantity') or request.GET.get('quantity', 1))
     
        donation = FoodDonation.objects.get(uuid=uuid)

        # Verify payment
     
        client = razorpay.Client(
     
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
     
        )

        params = {
     
            'razorpay_order_id': request.POST.get('razorpay_order_id'),
     
            'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
     
            'razorpay_signature': request.POST.get('razorpay_signature'),
        }

        try:
            client.utility.verify_payment_signature(params)

            # Payment verified — save claim
            amount_paid = donation.price * quantity

            FoodClaim.objects.create(
     
                donation=donation,
     
                recipient=request.user,
     
                quantity_claimed=quantity,
     
                amount_paid=amount_paid
            )

     
            donation.quantity_remaining -= quantity
     
            if donation.quantity_remaining <= 0:
     
                donation.status = 'Completed'
     
            donation.save()

            return redirect('my-claims')

        except razorpay.errors.SignatureVerificationError:
     
            return redirect('donation-detail', uuid=uuid)