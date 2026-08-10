from domains.parameters.models import TopicOption


class TopicOptionRepository:
    @staticmethod
    def get_all():
        return TopicOption.objects.all()

    @staticmethod
    def get_by_id(topic_option_id):
        try:
            return TopicOption.objects.get(pk=topic_option_id)
        except TopicOption.DoesNotExist:
            return None

    @staticmethod
    def create(data):
        topic_option = TopicOption(**data)
        topic_option.save()
        return topic_option

    @staticmethod
    def update(topic_option, data):
        for key, value in data.items():
            setattr(topic_option, key, value)
        topic_option.save()
        return topic_option

    @staticmethod
    def delete(topic_option):
        topic_option.delete()

    @staticmethod
    def description_exists(description, exclude_pk=None):
        queryset = TopicOption.objects.filter(description__iexact=description)
        if exclude_pk:
            queryset = queryset.exclude(pk=exclude_pk)
        return queryset.exists()