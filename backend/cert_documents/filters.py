# cert_documents/filters.py
import django_filters

from .models import CertLetter


class CertLetterFilter(django_filters.FilterSet):
    """
    Фильтрация писем CERT-CBU
    Параметры, которые ожидаем от фронта:

    - number:       частичное совпадение по номеру письма
    - subject:      частичное совпадение по теме
    - performer:    id исполнителя (пользователя)
    - date_from:    дата письма >= date_from
    - date_to:      дата письма <= date_to
    - has_deadline: true/false (есть установленный срок)
    - deadline_to:  deadline <= указанная дата
    - system:       система (по умолчанию "CERT-CBU", но можно фильтровать)
    """

    number = django_filters.CharFilter(
        field_name="number",
        lookup_expr="icontains",
    )

    subject = django_filters.CharFilter(
        field_name="subject",
        lookup_expr="icontains",
    )

    performer = django_filters.NumberFilter(
        field_name="performer_id"  # можно и "performer", но так явно
    )

    date_from = django_filters.DateFilter(
        field_name="date",
        lookup_expr="gte",
    )

    date_to = django_filters.DateFilter(
        field_name="date",
        lookup_expr="lte",
    )

    has_deadline = django_filters.BooleanFilter(
        field_name="has_deadline",
    )

    deadline_to = django_filters.DateFilter(
        field_name="deadline",
        lookup_expr="lte",
    )

    system = django_filters.CharFilter(
        field_name="system",
    )

    class Meta:
        model = CertLetter
        fields = [
            "number",
            "subject",
            "performer",
            "system",
            "has_deadline",
        ]
