from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F, FloatField, ExpressionWrapper
from .models import Campaign, Donation, CATEGORY_CHOICES 
from .forms import CampaignForm, DonationForm, RegisterForm, CampaignEditForm, UserUpdateForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .fraud_service import analyze_fraud

def campaign_index(request):
    campaigns = Campaign.objects.filter(is_active=True)

    query = request.GET.get('q')
    if query:
        campaigns = campaigns.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(creator__username__icontains=query)
        )

    category_filter = request.GET.get('category')
    if category_filter:
        campaigns = campaigns.filter(category=category_filter)

    campaigns = campaigns.annotate(
        percent=ExpressionWrapper(
            F('current_amount') * 100.0 / F('target_amount'),
            output_field=FloatField()
        )
    )

    sort_by = request.GET.get('sort', 'newest') 
    
    if sort_by == 'close_to_goal':
        campaigns = campaigns.filter(percent__lt=100).order_by('-percent')
    elif sort_by == 'oldest':
        campaigns = campaigns.order_by('created_at')
    else: 
        campaigns = campaigns.order_by('-created_at')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'main/campaign_list.html', {'campaigns': campaigns})

    return render(request, 'main/index.html', {
        'campaigns': campaigns,
        'categories': CATEGORY_CHOICES,
        'selected_category': category_filter,
        'current_sort': sort_by 
    })

def campaign_detail(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    donations = campaign.donations.filter(status='SUCCESS').order_by('-donated_at')
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to make a donation.')
            return redirect('login_user')

        form = DonationForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            user_wallet = request.user.userprofile 
            
            is_fraud, risk_score, risk_reason = analyze_fraud(request.user, amount, campaign)
            
            if is_fraud:
                donation = form.save(commit=False)
                donation.campaign = campaign
                donation.donor = request.user
                donation.status = 'FLAGGED'
                donation.risk_score = risk_score
                donation.risk_reason = risk_reason
                donation.save()
                
                messages.warning(request, f'Transaction held for security review. (Risk Score: {risk_score})')
                return redirect('campaign_detail', pk=pk)

            if user_wallet.balance >= amount:
                user_wallet.balance -= amount
                user_wallet.save()
                
                donation = form.save(commit=False)
                donation.campaign = campaign
                donation.donor = request.user
                donation.status = 'SUCCESS'
                donation.risk_score = risk_score
                donation.risk_reason = risk_reason
                donation.save()
                
                campaign.current_amount += amount
                campaign.save()
                
                fmt_amount = f"{amount:,.0f}".replace(",", ".")
                fmt_balance = f"{user_wallet.balance:,.0f}".replace(",", ".")

                messages.success(request, f'Success! Donation of Rp {fmt_amount} has been completed. Remaining balance: Rp {fmt_balance}.')
                return redirect('campaign_detail', pk=pk)
            else:
                messages.error(request, 'Insufficient balance. Please request an account top-up from an administrator.')
                
    else:
        form = DonationForm()

    return render(request, 'main/detail.html', {
        'campaign': campaign,
        'donations': donations,
        'form': form
    })

@login_required(login_url='/admin/')
def create_campaign(request):
    if request.method == 'POST':
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.creator = request.user
            campaign.save()
            return redirect('campaign_index')
    else:
        form = CampaignForm()
    return render(request, 'main/create.html', {'form': form})

@login_required
def edit_campaign(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)

    if campaign.creator != request.user:
        messages.error(request, "You are not the owner of this campaign.")
        return redirect('campaign_index')

    if request.method == 'POST':
        if 'btn_end_campaign' in request.POST:
            campaign.is_active = False
            campaign.save()
            messages.success(request, 'Campaign has been successfully closed.')
            return redirect('profile_dashboard')

        form = CampaignEditForm(request.POST, instance=campaign)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campaign updated successfully.')
            return redirect('profile_dashboard')
    else:
        form = CampaignEditForm(instance=campaign)

    return render(request, 'main/edit_campaign.html', {'form': form, 'campaign': campaign})

def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('campaign_index')
    else:
        form = RegisterForm()
    return render(request, 'main/register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('campaign_index')
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('login_user')

@login_required
def my_campaigns(request):
    campaigns = Campaign.objects.filter(creator=request.user).order_by('-created_at')
    
    total_raised = sum(c.current_amount for c in campaigns)
    
    return render(request, 'main/my_campaigns.html', {
        'campaigns': campaigns,
        'total_raised': total_raised
    })
    
@login_required
def profile_dashboard(request):
    campaigns = Campaign.objects.filter(creator=request.user).order_by('-created_at')
    total_raised = sum(c.current_amount for c in campaigns)

    if request.method == 'POST':
        if 'btn_update_profile' in request.POST:
            p_form = UserUpdateForm(request.POST, instance=request.user)
            pass_form = PasswordChangeForm(request.user)
            if p_form.is_valid():
                p_form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('profile_dashboard')

        elif 'btn_change_password' in request.POST:
            pass_form = PasswordChangeForm(request.user, request.POST)
            p_form = UserUpdateForm(instance=request.user)
            if pass_form.is_valid():
                user = pass_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully.')
                return redirect('profile_dashboard')

    else:
        p_form = UserUpdateForm(instance=request.user)
        pass_form = PasswordChangeForm(request.user)

    return render(request, 'main/profile.html', {
        'campaigns': campaigns,
        'total_raised': total_raised,
        'p_form': p_form,
        'pass_form': pass_form
    })