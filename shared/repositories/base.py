from django.core.exceptions import ObjectDoesNotExist


class BaseRepository:
    model = None

    @classmethod
    def get_by_id(cls, id):
        try:
            return cls.model.objects.get(pk=id)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def list_all(cls):
        return cls.model.objects.all()

    @classmethod
    def get_active(cls):
        return cls.model.objects.filter(is_active=True)

    @classmethod
    def create(cls, data):
        obj = cls.model(**data)
        obj.save()
        return obj

    @classmethod
    def update(cls, obj, data):
        for key, value in data.items():
            setattr(obj, key, value)
        obj.save()
        return obj

    @classmethod
    def delete(cls, obj):
        obj.delete()
