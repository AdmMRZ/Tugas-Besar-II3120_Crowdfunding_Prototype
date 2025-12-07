from django.utils import timezone
from datetime import timedelta
from .models import Donation

def analyze_fraud(user, amount, campaign):
    score = 0
    reasons = []
    
    if (timezone.now() - user.date_joined).days < 1:
        score += 25
        reasons.append("New Account (<24h)")

    five_mins_ago = timezone.now() - timedelta(minutes=5)
    recent_donations = Donation.objects.filter(donor=user, donated_at__gte=five_mins_ago).count()
    
    if recent_donations >= 3:
        score += 40
        reasons.append("High Velocity (3+ tx in 5m)")
    elif recent_donations >= 1:
        score += 10

    if amount > 10000000:
        score += 50
        reasons.append("Large Amount (>10jt)")
    elif amount > 5000000:
        score += 20
        reasons.append("Medium Amount (>5jt)")

    is_fraud = score >= 50
    return is_fraud, score, ", ".join(reasons)