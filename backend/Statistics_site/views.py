# Statistics_site/views.py
from collections import defaultdict
from datetime import date

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models.functions import TruncMonth

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from cert_documents.models import CertLetter, CertLetterReply

User = get_user_model()


class CertStatisticsViewSet(viewsets.ViewSet):
    """
    Статистика по письмам CERT-CBU и работе организаций.
    Все методы только на чтение.
    """
    permission_classes = [permissions.IsAuthenticated]

    # 1) Кол-во писем CERT-CBU по месяцам
    @action(detail=False, methods=["get"], url_path="letters-by-month")
    def letters_by_month(self, request):
        """
        GET /api/statistics/cert/letters-by-month/?year=2025
        Опционально:
          - year: конкретный год
          - date_from, date_to: диапазон дат (yyyy-mm-dd)
        """
        qs = CertLetter.objects.filter(system="CERT-CBU")

        year = request.query_params.get("year")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        if year:
            qs = qs.filter(date__year=year)

        if date_from:
            qs = qs.filter(date__gte=date_from)

        if date_to:
            qs = qs.filter(date__lte=date_to)

        # Группировка по месяцам
        agg = (
            qs.annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

        data = []
        for row in agg:
            m = row["month"]
            data.append({
                "month": m.strftime("%Y-%m"),     # 2025-01
                "year": m.year,
                "month_num": m.month,
                "count": row["count"],
            })

        return Response({"results": data})

    # 2) Кол-во сотрудников CERT-CBU
    @action(detail=False, methods=["get"], url_path="employees-count")
    def employees_count(self, request):
        """
        GET /api/statistics/cert/employees-count/
        Возвращает общее количество сотрудников.

        ⚠️ ВАЖНО:
        Сейчас считает всех активных пользователей.
        При необходимости сузить до CERT-CBU
        можно добавить фильтры (по отделу/ролям/группе).
        """
        # TODO: здесь можно добавить свои фильтры для CERT-CBU
        # например, если есть поле user.department == "CERT-CBU"
        # employees_qs = User.objects.filter(is_active=True, department="CERT-CBU")

        employees_qs = User.objects.filter(is_active=True)
        total = employees_qs.count()

        return Response({
            "total_employees": total,
        })

    # 3) Статистика: какие организации отвечают вовремя / с опозданием / не отвечают
    @action(detail=False, methods=["get"], url_path="org-replies")
    def org_replies_stats(self, request):
        """
        GET /api/statistics/cert/org-replies/?date_from=2025-01-01&date_to=2025-12-31

        Считает по организациям:
          - сколько писем с обязательным ответом (need_replies=True)
          - сколько ответов:
              * вовремя (до/включая deadline)
              * с опозданием (после deadline)
              * без ответа
        Письма с need_replies=False НЕ учитываются.
        """
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        letters_qs = CertLetter.objects.filter(
            system="CERT-CBU",
            need_replies=True,          # 🔹 учитываем только письма, где нужны ответы
        ).prefetch_related(
            "dest_organizations",
            "replies__organization",
        )

        if date_from:
            letters_qs = letters_qs.filter(date__gte=date_from)
        if date_to:
            letters_qs = letters_qs.filter(date__lte=date_to)

        stats = {}  # org_id -> данные

        for letter in letters_qs:
            # Для "во время / не во время" логично учитывать только письма со сроком
            if not letter.has_deadline or not letter.deadline:
                # Если хочешь, можно добавить сюда отдельную логику,
                # например считать просто "ответил / не ответил без срока".
                continue

            deadline = letter.deadline

            # Все организации, которым отправлено это письмо
            dest_orgs = list(letter.dest_organizations.all())

            # Все ответы по этому письму (один или несколько от разных орг)
            replies = list(letter.replies.all())

            for org in dest_orgs:
                org_id = org.id
                if not org_id:
                    continue

                if org_id not in stats:
                    stats[org_id] = {
                        "organization_id": org_id,
                        "organization_name": getattr(org, "name", str(org)),
                        "on_time": 0,      # ответ вовремя
                        "late": 0,         # ответ с опозданием
                        "no_reply": 0,     # нет ответа
                        "total_required": 0,   # всего писем, по которым нужен ответ
                    }

                stats[org_id]["total_required"] += 1

                # ответы именно этой организации на данное письмо
                org_replies = [
                    r for r in replies
                    if r.organization_id == org_id and r.received_date
                ]

                if not org_replies:
                    stats[org_id]["no_reply"] += 1
                    continue

                # берём самую раннюю дату получения ответа
                earliest = min(r.received_date for r in org_replies)

                if earliest <= deadline:
                    stats[org_id]["on_time"] += 1
                else:
                    stats[org_id]["late"] += 1

        # Переводим в список
        result = list(stats.values())

        # Можно отсортировать, например, по доле вовремя
        # (on_time / total_required) в убывающем порядке
        for item in result:
            tr = item["total_required"] or 1
            item["on_time_ratio"] = round(item["on_time"] / tr, 3)

        result.sort(key=lambda x: x["on_time_ratio"], reverse=True)

        return Response({"results": result})
