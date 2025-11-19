import dateutil.parser
import pytz
from django import forms
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django_scopes.forms import SafeModelChoiceField
from i18nfield.forms import I18nModelFormSet
from phonenumber_field.formfields import PhoneNumberField
from pretix.base.forms import I18nModelForm
from pretix.base.forms.questions import (
    MaxDateTimeValidator,
    MaxDateValidator,
    MinDateTimeValidator,
    MinDateValidator,
    QuestionCheckboxSelectMultiple,
    WrappedPhoneNumberPrefixWidget,
)
from pretix.base.forms.widgets import (
    DatePickerWidget,
    SplitDateTimePickerWidget,
    TimePickerWidget,
)
from pretix.base.models.items import Question
from pretix.control.forms import SplitDateTimeField
from pretix.helpers.countries import CachedCountries
from pretix.helpers.i18n import get_format_without_seconds

from .models import PlaceholderRule, QuestionPlaceholder


class QuestionPlaceholderCreateForm(forms.ModelForm):
    def __init__(self, *args, event=None, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)
        self.fields["question"].queryset = Question.objects.filter(event=event)

    def clean_slug(self):
        value = self.cleaned_data.get("slug")
        qs = QuestionPlaceholder.objects.filter(question__event=self.event)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.pk)
        if value and qs.filter(slug=value).exists():
            raise forms.ValidationError(_("This slug is already in use!"))
        if qs.filter(
            slug__isnull=True, question_id=self.cleaned_data.get("question").id
        ).exists():
            raise forms.ValidationError(
                _(
                    "This question already has a placeholder – please choose a slug to be able to tell them apart!"
                )
            )
        return value

    class Meta:
        model = QuestionPlaceholder
        fields = ("question", "slug")
        field_classes = {
            "question": SafeModelChoiceField,
        }


class QuestionPlaceholderEditForm(I18nModelForm):
    class Meta:
        model = QuestionPlaceholder
        fields = ("fallback_content", "use_fallback_when_unanswered")


class PlaceholderRuleForm(I18nModelForm):
    def __init__(self, *args, placeholder=None, event=None, **kwargs):
        self.placeholder = placeholder
        self.event = event
        super().__init__(*args, **kwargs)
        # Set appropriate options for the question type
        allowed = PlaceholderRule.get_allowed_methods(placeholder.question.type)
        initial = self.instance.condition_content if self.instance else None
        self.fields["condition_operation"] = forms.ChoiceField(
            choices=(
                (choice, _)
                for choice, _ in PlaceholderRule.ComparisonOperation.choices
                if choice in allowed
            ),
            label="If the user's answer is",
        )
        self.fields["condition_content"] = self.get_content_field(
            placeholder.question, initial=initial
        )
        self.fields["content"].label = "Then add this content to the email"

    def get_content_field(self, q, initial):
        tz = pytz.timezone(self.placeholder.question.event.settings.timezone)
        label = ""
        help_text = ""
        required = False
        if q.type == Question.TYPE_BOOLEAN:
            widget = forms.CheckboxInput()
            initialbool = initial == "True"
            return forms.BooleanField(
                label=label,
                required=False,
                help_text=help_text,
                initial=initialbool,
                widget=widget,
            )
        if q.type == Question.TYPE_NUMBER:
            return forms.DecimalField(
                label=label,
                required=required,
                help_text=q.help_text,
                initial=initial,
            )
        if q.type == Question.TYPE_STRING:
            return forms.CharField(
                label=label,
                required=required,
                help_text=help_text,
                initial=initial,
            )
        if q.type == Question.TYPE_TEXT:
            return forms.CharField(
                label=label,
                required=required,
                help_text=help_text,
                widget=forms.Textarea,
                initial=initial,
            )
        if q.type == Question.TYPE_COUNTRYCODE:
            return CountryField(
                countries=CachedCountries,
                blank=True,
                null=True,
                blank_label=" ",
            ).formfield(
                label=label,
                required=required,
                help_text=help_text,
                widget=forms.Select,
                empty_label=" ",
                initial=initial,
            )
        if q.type == Question.TYPE_CHOICE:
            return forms.ModelChoiceField(
                queryset=q.options,
                label=label,
                required=required,
                help_text=help_text,
                widget=forms.Select,
                to_field_name="identifier",
                empty_label="",
                initial=q.options.filter(pk=initial).first() if initial else None,
            )
        elif q.type == Question.TYPE_CHOICE_MULTIPLE:
            return forms.ModelMultipleChoiceField(
                queryset=q.options,
                label=label,
                required=required,
                help_text=help_text,
                to_field_name="identifier",
                widget=QuestionCheckboxSelectMultiple,
                initial=initial,
            )
        elif q.type == Question.TYPE_DATE:
            attrs = {}
            if q.valid_date_min:
                attrs["data-min"] = q.valid_date_min.isoformat()
            if q.valid_date_max:
                attrs["data-max"] = q.valid_date_max.isoformat()
            field = forms.DateField(
                label=label,
                required=required,
                help_text=help_text,
                initial=dateutil.parser.parse(initial).date()
                if initial and initial
                else None,
                widget=DatePickerWidget(attrs),
            )
            if q.valid_date_min:
                field.validators.append(MinDateValidator(q.valid_date_min))
            if q.valid_date_max:
                field.validators.append(MaxDateValidator(q.valid_date_max))
            return field
        elif q.type == Question.TYPE_TIME:
            return forms.TimeField(
                label=label,
                required=required,
                help_text=help_text,
                initial=dateutil.parser.parse(initial).time()
                if initial and initial
                else None,
                widget=TimePickerWidget(
                    time_format=get_format_without_seconds("TIME_INPUT_FORMATS")
                ),
            )
        elif q.type == Question.TYPE_DATETIME:
            field = SplitDateTimeField(
                label=label,
                required=required,
                help_text=help_text,
                initial=dateutil.parser.parse(initial).astimezone(tz)
                if initial
                else None,
                widget=SplitDateTimePickerWidget(
                    time_format=get_format_without_seconds("TIME_INPUT_FORMATS"),
                    min_date=q.valid_datetime_min,
                    max_date=q.valid_datetime_max,
                ),
            )
            if q.valid_datetime_min:
                field.validators.append(MinDateTimeValidator(q.valid_datetime_min))
            if q.valid_datetime_max:
                field.validators.append(MaxDateTimeValidator(q.valid_datetime_max))
            return field
        elif q.type == Question.TYPE_PHONENUMBER:
            return PhoneNumberField(
                label=label,
                required=required,
                help_text=help_text,
                initial=initial,
                widget=WrappedPhoneNumberPrefixWidget(),
            )

    def clean_condition_content(self):
        content = self.cleaned_data.get("condition_content")
        if content:
            content = self.placeholder.question.clean_answer(content)
            if hasattr(content, "pk"):
                return content.pk
            return content

    def save(self, *args, **kwargs):
        self.instance.condition_content = self.cleaned_data.get("condition_content")
        return super().save(*args, **kwargs)

    class Meta:
        model = PlaceholderRule
        fields = ("content", "condition_operation")


class I18nPlaceholderFormSet(I18nModelFormSet):
    def __init__(self, *args, **kwargs):
        self.placeholder = kwargs.pop("placeholder", None)
        self.event = kwargs.pop("event", None)
        kwargs["locales"] = self.event.settings.locales if self.event else ["en"]
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, *args):
        result = super().get_form_kwargs(*args)
        result["placeholder"] = self.placeholder
        return result

    def _construct_form(self, i, **kwargs):
        kwargs["locales"] = self.locales
        kwargs["placeholder"] = self.placeholder
        kwargs["event"] = self.event
        return super()._construct_form(i, **kwargs)
