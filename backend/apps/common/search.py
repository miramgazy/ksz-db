from rest_framework.filters import SearchFilter
from django.db.models import Q
from .keyboard import get_search_variants


class SmartSearchFilter(SearchFilter):
    """
    SearchFilter with bilingual layout switching (QWERTY <-> JCUKEN)
    and Kazakh letter normalization.
    """

    def filter_queryset(self, request, queryset, view):
        search_terms = self.get_search_terms(request)
        if not search_terms:
            return queryset

        fields = getattr(view, 'search_fields', None)
        if not fields:
            return queryset

        combined_q = Q()
        for term in search_terms:
            variants = get_search_variants(term)
            term_q = Q()
            for variant in variants:
                for field_name in fields:
                    term_q |= Q(**{f"{field_name}__icontains": variant})
            combined_q &= term_q

        return queryset.filter(combined_q)
