from django.dispatch import receiver
from django.urls import resolve, reverse
from django.utils.translation import gettext_lazy as _
from pretix.base.models import QuestionOption
from pretix.base.signals import event_copy_data, register_mail_placeholders
from pretix.control.signals import nav_event

from .models import QuestionPlaceholder
from .placeholder import QuestionMailPlaceholder


def get_placeholders_for_event(event):
    return QuestionPlaceholder.objects.filter(question__event=event)


@receiver(register_mail_placeholders, dispatch_uid="placeholder_custom")
def register_mail_question_placeholders(sender, **kwargs):
    return [
        QuestionMailPlaceholder(placeholder)
        for placeholder in get_placeholders_for_event(sender)
    ]


@receiver(event_copy_data, dispatch_uid="question_placeholders_clone")
def copy_event_placeholders(sender, other, question_map, **kwargs):
    for placeholder in QuestionPlaceholder.objects.filter(question__event=other):
        old_question = placeholder.question

        rules = list(placeholder.rules.all())
        placeholder.pk = None
        placeholder.question = question_map[placeholder.question_id]
        placeholder.save()

        has_options = old_question.type in (
            placeholder.question.TYPE_CHOICE,
            placeholder.question.TYPE_CHOICE_MULTIPLE,
        )
        option_map = {}  # old_id to new ID
        if has_options:
            for option in old_question.options.all():
                option_map[str(option.pk)] = QuestionOption.objects.filter(
                    identifier=option.identifier, question=placeholder.question
                ).first()

        for rule in rules:
            rule.pk = None
            rule.placeholder = placeholder
            if has_options:
                option = option_map.get(rule.condition_content)
                if option:
                    rule.condition_content = str(option.pk)
            rule.save()


@receiver(nav_event, dispatch_uid="question_placeholders_nav")
def navbar_info(sender, request, **kwargs):
    url = resolve(request.path_info)
    if not request.user.has_event_permission(
        request.organizer, request.event, "can_change_event_settings"
    ):
        return []
    return [
        {
            "label": _("Email placeholders"),
            "icon": "question-circle-o",
            "url": reverse(
                "plugins:pretix_question_placeholders:list",
                kwargs={
                    "event": request.event.slug,
                    "organizer": request.organizer.slug,
                },
            ),
            "active": url.namespace == "plugins:pretix_question_placeholders",
        }
    ]
