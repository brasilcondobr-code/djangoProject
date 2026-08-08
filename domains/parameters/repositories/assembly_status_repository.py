from domains.parameters.models import AssemblyStatus


class AssemblyStatusRepository:
    @staticmethod
    def get_all():
        return AssemblyStatus.objects.all()

    @staticmethod
    def get_by_id(assembly_status_id):
        try:
            return AssemblyStatus.objects.get(pk=assembly_status_id)
        except AssemblyStatus.DoesNotExist:
            return None

    @staticmethod
    def create(data):
        assembly_status = AssemblyStatus(**data)
        assembly_status.save()
        return assembly_status

    @staticmethod
    def update(assembly_status, data):
        for key, value in data.items():
            setattr(assembly_status, key, value)
        assembly_status.save()
        return assembly_status

    @staticmethod
    def delete(assembly_status):
        assembly_status.delete()

    @staticmethod
    def description_exists(description, exclude_pk=None):
        queryset = AssemblyStatus.objects.filter(description__iexact=description)
        if exclude_pk:
            queryset = queryset.exclude(pk=exclude_pk)
        return queryset.exists()

    @staticmethod
    def running_exists(exclude_pk=None):
        queryset = AssemblyStatus.objects.filter(is_running=True)
        if exclude_pk:
            queryset = queryset.exclude(pk=exclude_pk)
        return queryset.exists()

    @staticmethod
    def complete_exists(exclude_pk=None):
        queryset = AssemblyStatus.objects.filter(is_complete=True)
        if exclude_pk:
            queryset = queryset.exclude(pk=exclude_pk)
        return queryset.exists()