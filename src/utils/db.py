def dictfetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def paginate_queryset(queryset, page, limit=10):
    pages = ((queryset.count() - 1) // limit) + 1
    if page and page > 0:
        offset = (page - 1) * limit
        limit = offset + limit
        return pages, queryset[offset:limit]
    return pages, queryset
