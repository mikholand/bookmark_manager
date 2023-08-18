menu = [{'title': "Добавить закладку", 'url_name': 'add_bookmark'},
        {'title': "Мои коллекции", 'url_name': 'collections'},
        ]


class DataMixin:
    paginate_by = 100

    def get_user_context(self, **kwargs):
        context = kwargs
        context['menu'] = menu

        return context
