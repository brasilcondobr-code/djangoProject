class BaseSelector:
    model = None

    @classmethod
    def get_all_active(cls):
        return cls.model.objects.filter(is_active=True)

    @classmethod
    def get_by_id(cls, id):
        return cls.model.objects.filter(pk=id).first()

    @classmethod
    def get_by_field(cls, field, value):
        return cls.model.objects.filter(**{field: value}).first()
