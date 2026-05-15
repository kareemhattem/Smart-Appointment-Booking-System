from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from accounts.models import User
from .models import ProviderProfile, AvailabilitySlot, Category
from .forms import ProviderProfileForm, AvailabilitySlotForm


def provider_list(request):
    providers = User.objects.filter(role='provider').select_related('provider_profile__category')
    categories = Category.objects.all()

    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    min_rating = request.GET.get('min_rating', '')

    if search:
        providers = providers.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(provider_profile__specialization__icontains=search) |
            Q(provider_profile__title__icontains=search)
        )

    if category_id:
        providers = providers.filter(provider_profile__category_id=category_id)

    provider_data = []
    for p in providers:
        try:
            profile = p.provider_profile
            avg = p.received_reviews.aggregate(avg=Avg('rating'))['avg'] or 0
            if min_rating and avg < float(min_rating):
                continue
            provider_data.append({'user': p, 'profile': profile, 'avg_rating': round(avg, 1)})
        except ProviderProfile.DoesNotExist:
            pass

    return render(request, 'providers/list.html', {
        'providers': provider_data,
        'categories': categories,
        'search': search,
        'selected_category': category_id,
        'min_rating': min_rating,
    })


def provider_detail(request, pk):
    provider = get_object_or_404(User, pk=pk, role='provider')
    try:
        profile = provider.provider_profile
    except ProviderProfile.DoesNotExist:
        profile = None

    slots = AvailabilitySlot.objects.filter(provider=provider, is_active=True)
    reviews = provider.received_reviews.select_related('reviewer').all()[:10]
    avg_rating = provider.received_reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    return render(request, 'providers/detail.html', {
        'provider': provider,
        'profile': profile,
        'slots': slots,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
    })


@login_required
def manage_profile(request):
    if not request.user.is_provider():
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    profile, _ = ProviderProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProviderProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Provider profile updated.')
            return redirect('providers:manage_profile')
    else:
        form = ProviderProfileForm(instance=profile)

    return render(request, 'providers/manage_profile.html', {'form': form, 'profile': profile})


@login_required
def manage_slots(request):
    if not request.user.is_provider():
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    slots = AvailabilitySlot.objects.filter(provider=request.user)

    if request.method == 'POST':
        form = AvailabilitySlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.provider = request.user
            slot.save()
            messages.success(request, 'Availability slot added.')
            return redirect('providers:manage_slots')
    else:
        form = AvailabilitySlotForm()

    return render(request, 'providers/manage_slots.html', {'form': form, 'slots': slots})


@login_required
def delete_slot(request, pk):
    if not request.user.is_provider():
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    slot = get_object_or_404(AvailabilitySlot, pk=pk, provider=request.user)
    slot.delete()
    messages.success(request, 'Slot removed.')
    return redirect('providers:manage_slots')
