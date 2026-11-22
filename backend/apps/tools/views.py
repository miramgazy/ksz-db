import secrets
import string
from collections import Counter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from apps.companies.models import Company, AnydeskStation
from apps.accounts.models import User

class PasswordGeneratorView(APIView):
    """
    Generates a cryptographically strong random password.
    Configurable length and character set.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        try:
            length = int(request.query_params.get('length', 12))
            length = max(6, min(length, 64))
        except (ValueError, TypeError):
            length = 12

        include_digits = request.query_params.get('digits', 'true').lower() in ('true', '1')
        include_upper = request.query_params.get('upper', 'true').lower() in ('true', '1')
        include_lower = request.query_params.get('lower', 'true').lower() in ('true', '1')
        include_symbols = request.query_params.get('symbols', 'true').lower() in ('true', '1')

        chars = ''
        guaranteed = []

        if include_upper:
            chars += string.ascii_uppercase
            guaranteed.append(secrets.choice(string.ascii_uppercase))
        if include_lower:
            chars += string.ascii_lowercase
            guaranteed.append(secrets.choice(string.ascii_lowercase))
        if include_digits:
            chars += string.digits
            guaranteed.append(secrets.choice(string.digits))
        if include_symbols:
            # Safe special symbols commonly used in passwords
            symbols = '!@#$%^&*()-_=+'
            chars += symbols
            guaranteed.append(secrets.choice(symbols))

        if not chars:
            chars = string.ascii_letters + string.digits

        remaining_length = max(0, length - len(guaranteed))
        password_chars = guaranteed + [secrets.choice(chars) for _ in range(remaining_length)]
        secrets.SystemRandom().shuffle(password_chars)
        password = ''.join(password_chars)

        return Response({
            'password': password,
            'length': len(password),
        })


class DashboardStatsView(APIView):
    """
    Returns high-level statistics for the dashboard.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        total_companies = Company.objects.count()
        active_companies = Company.objects.filter(status=True).count()
        inactive_companies = total_companies - active_companies
        total_stations = AnydeskStation.objects.count()

        pending_users_count = 0
        if request.user.role == User.Roles.SUPERADMIN:
            pending_users_count = User.objects.filter(registration_status=User.RegistrationStatus.PENDING).count()

        top_cities = list(
            Company.objects.exclude(city='')
            .values_list('city', flat=True)
        )
        city_counter = Counter(top_cities).most_common(5)

        top_types = list(
            Company.objects.exclude(business_type='')
            .values_list('business_type', flat=True)
        )
        type_counter = Counter(top_types).most_common(5)

        return Response({
            'total_companies': total_companies,
            'active_companies': active_companies,
            'inactive_companies': inactive_companies,
            'total_stations': total_stations,
            'pending_users_count': pending_users_count,
            'top_cities': [{'name': c[0], 'count': c[1]} for c in city_counter],
            'top_business_types': [{'name': t[0], 'count': t[1]} for t in type_counter],
        })
