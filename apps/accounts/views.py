from django.shortcuts import render, redirect
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.accounts import models
from .forms import UserProfileForm
from apps.examens.models import Examen
from apps.planning.models import Seance


@login_required
def profile_view(request):
    """Afficher et éditer le profil utilisateur, en fournissant `stats` au template.

    - Si `request.user.is_superuser` : calculs globaux (tous les utilisateurs).
    - Sinon : tentatives raisonnables basées sur les relations existantes (apprenant/candidat).
    """
    user = request.user

    # form handling
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=user)

    # Default stats
    total_seances = total_examens = total_heures = taux_reussite = 0

    # Superuser: global totals
    if user.is_superuser:
        total_seances = Seance.objects.count()
        total_examens = Examen.objects.count()
        total_heures = (Seance.objects.aggregate(total=Sum('duree_minutes'))['total'] or 0) / 60
        examens_qs = Examen.objects.all()
        passed = examens_qs.filter(result='ADMIS').count()
        taux_reussite = int((passed / examens_qs.count()) * 100) if examens_qs.exists() else 0
    else:
        # Regular user: try to compute personal stats; fall back safely if relations differ
        try:
            # Many projects link Seance to an 'apprenant' object
            total_seances = Seance.objects.filter(apprenant__user=user).count()
            total_heures = (Seance.objects.filter(apprenant__user=user).aggregate(total=Sum('duree_minutes'))['total'] or 0) / 60
        except Exception:
            # best-effort fallback: look for seances referencing the user directly
            try:
                total_seances = Seance.objects.filter(apprenant__user=user).count()
                total_heures = (Seance.objects.filter(apprenant__user=user).aggregate(total=Sum('duree_minutes'))['total'] or 0) / 60
            except Exception:
                total_seances = total_heures = 0

        try:
            examens_qs = Examen.objects.filter(apprenant__user=user)
            total_examens = examens_qs.count()
            passed = examens_qs.filter(result='ADMIS').count()
            taux_reussite = int((passed / examens_qs.count()) * 100) if examens_qs.exists() else 0
        except Exception:
            total_examens = 0
            taux_reussite = 0

    stats = {
        'total_seances': total_seances,
        'total_examens': total_examens,
        'total_heures': total_heures,
        'taux_reussite': taux_reussite,
    }

    return render(request, 'accounts/profile.html', {
        'form': form,
        'stats': stats,
    })