from django.db import migrations


def copy_email_schedules(apps, schema_editor):
    OldSchedule = apps.get_model('administrative', 'VirtualMeetingEmailSchedule')
    OldRecipient = apps.get_model('administrative', 'VirtualMeetingEmailRecipient')
    Task = apps.get_model('data_management', 'ScheduledTaskModule')
    Recipient = apps.get_model('data_management', 'ScheduledTaskRecipient')
    VirtualMeeting = apps.get_model('administrative', 'VirtualMeeting')

    for old in OldSchedule.objects.all().order_by('pk'):
        if old.virtual_meeting_id is None:
            continue
        try:
            vm = VirtualMeeting.objects.get(pk=old.virtual_meeting_id)
        except VirtualMeeting.DoesNotExist:
            continue
        task, created = Task.objects.get_or_create(
            virtual_meeting=vm,
            task_type=old.email_type,
            defaults={
                'scheduled_at': old.scheduled_at,
                'status': old.status,
                'attempts': old.attempts,
                'sent_at': old.sent_at,
                'last_error': old.last_error,
                'celery_task_id': old.celery_task_id,
            },
        )
        if created:
            Task.objects.filter(pk=task.pk).update(
                created_at=old.created_at,
                updated_at=old.updated_at,
            )
        for old_recipient in OldRecipient.objects.filter(schedule=old):
            recipient, created = Recipient.objects.get_or_create(
                task=task,
                resident_id=old_recipient.resident_id,
                defaults={
                    'email': old_recipient.email,
                    'status': old_recipient.status,
                    'sent_at': old_recipient.sent_at,
                    'last_error': old_recipient.last_error,
                },
            )
            if created:
                Recipient.objects.filter(pk=recipient.pk).update(
                    created_at=old_recipient.created_at,
                    updated_at=old_recipient.updated_at,
                )


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('administrative', '0038_virtualmeetingemailschedule_and_more'),
        ('data_management', '0006_scheduledtaskmodule_fields_scheduledtaskrecipient'),
    ]

    operations = [
        migrations.RunPython(copy_email_schedules, reverse_noop),
        migrations.RemoveField(
            model_name='virtualmeetingemailschedule',
            name='virtual_meeting',
        ),
        migrations.DeleteModel(
            name='VirtualMeetingEmailRecipient',
        ),
        migrations.DeleteModel(
            name='VirtualMeetingEmailSchedule',
        ),
    ]