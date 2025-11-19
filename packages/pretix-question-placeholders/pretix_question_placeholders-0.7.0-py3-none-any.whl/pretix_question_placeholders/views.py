from django.contrib import messages
from django.db import transaction
from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from pretix.control.permissions import EventPermissionRequiredMixin

from .forms import (
    I18nPlaceholderFormSet,
    PlaceholderRuleForm,
    QuestionPlaceholderCreateForm,
    QuestionPlaceholderEditForm,
)
from .models import PlaceholderRule, QuestionPlaceholder


class QuestionPlaceholderList(EventPermissionRequiredMixin, ListView):
    permission = "can_change_event_settings"
    template_name = "pretix_question_placeholders/list.html"
    context_object_name = "question_placeholders"
    model = QuestionPlaceholder

    def get_queryset(self):
        from .signals import get_placeholders_for_event

        return get_placeholders_for_event(self.request.event)


class QuestionPlaceholderCreate(EventPermissionRequiredMixin, CreateView):
    permission = "can_change_event_settings"
    form_class = QuestionPlaceholderCreateForm
    template_name = "pretix_question_placeholders/create.html"
    model = QuestionPlaceholder

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result["event"] = self.request.event
        return result

    def form_valid(self, form):
        self.form = form
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "plugins:pretix_question_placeholders:show",
            kwargs={
                "organizer": self.request.event.organizer.slug,
                "event": self.request.event.slug,
                "pk": self.form.instance.pk,
            },
        )


class QuestionPlaceholderEdit(EventPermissionRequiredMixin, UpdateView):
    permission = "can_change_event_settings"
    template_name = "pretix_question_placeholders/edit.html"
    form_class = QuestionPlaceholderEditForm
    model = QuestionPlaceholder

    def get_object(self):
        from .signals import get_placeholders_for_event

        return get_object_or_404(
            get_placeholders_for_event(self.request.event), pk=self.kwargs["pk"]
        )

    def get_success_url(self):
        return reverse(
            "plugins:pretix_question_placeholders:show",
            kwargs={
                "organizer": self.request.event.organizer.slug,
                "event": self.request.event.slug,
                "pk": self.get_object().pk,
            },
        )

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result["formset"] = self.formset
        return result

    def get_form_kwargs(self, **kwargs):
        result = super().get_form_kwargs(**kwargs)
        result["locales"] = self.request.event.settings.locales
        return result

    @cached_property
    def formset(self):
        formsetclass = inlineformset_factory(
            QuestionPlaceholder,
            PlaceholderRule,
            form=PlaceholderRuleForm,
            formset=I18nPlaceholderFormSet,
            extra=0,
            can_delete=True,
            can_order=True,
        )
        return formsetclass(
            self.request.POST if self.request.method == "POST" else None,
            queryset=PlaceholderRule.objects.filter(placeholder=self.get_object()),
            event=self.request.event,
            placeholder=self.get_object(),
        )

    def save_formset(self, obj):
        if self.formset.is_valid():
            for form in self.formset.initial_forms:
                if form in self.formset.deleted_forms:
                    if not form.instance.pk:
                        continue
                    form.instance.delete()
                    form.instance.pk = None

            forms = self.formset.ordered_forms + [
                ef
                for ef in self.formset.extra_forms
                if ef not in self.formset.ordered_forms
                and ef not in self.formset.deleted_forms
            ]
            for i, form in enumerate(forms):
                form.instance.position = i
                form.instance.placeholder = obj
                form.save()

            return True
        return False

    @transaction.atomic
    def form_valid(self, form):
        super().form_valid(form)
        if not self.save_formset(self.get_object()):
            return self.get(self.request, *self.args, **self.kwargs)
        messages.success(self.request, _("Your changes have been saved."))
        return redirect(
            reverse(
                "plugins:pretix_question_placeholders:list",
                kwargs={
                    "organizer": self.request.event.organizer.slug,
                    "event": self.request.event.slug,
                },
            )
        )


class QuestionPlaceholderDelete(EventPermissionRequiredMixin, DeleteView):
    permission = "can_change_event_settings"
    template_name = "pretix_question_placeholders/delete.html"
    model = QuestionPlaceholder

    def get_object(self):
        from .signals import get_placeholders_for_event

        return get_object_or_404(
            get_placeholders_for_event(self.request.event), pk=self.kwargs["pk"]
        )

    def get_success_url(self):
        return reverse(
            "plugins:pretix_question_placeholders:list",
            kwargs={
                "organizer": self.request.event.organizer.slug,
                "event": self.request.event.slug,
            },
        )
