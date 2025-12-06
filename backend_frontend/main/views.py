from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .models import Campaign, Donation
from .forms import CampaignForm, DonationForm, RegisterForm, UserUpdateForm

def campaign_index(request):
    campaigns = Campaign.objects.all().order_by('-created_at')
    return render(request, 'main/index.html', {'campaigns': campaigns})

def campaign_detail(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    donations = campaign.donations.all().order_by('-donated_at')
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to make a donation.')
            return redirect('login_user')

        form = DonationForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            user_wallet = request.user.userprofile 
            
            if user_wallet.balance >= amount:
                user_wallet.balance -= amount
                user_wallet.save()
                
                donation = form.save(commit=False)
                donation.campaign = campaign
                donation.donor = request.user
                donation.save()
                
                campaign.current_amount += amount
                campaign.save()
                
                messages.success(request, f'Success! Donation of Rp {amount} has been completed. Remaining balance: Rp {user_wallet.balance}.')
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

