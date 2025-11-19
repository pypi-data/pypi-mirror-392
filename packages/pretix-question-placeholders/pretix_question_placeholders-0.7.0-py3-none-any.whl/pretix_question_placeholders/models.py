import warnings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_scopes import ScopedManager
from i18nfield.fields import I18nTextField
from pretix.base.models import Question


class QuestionPlaceholder(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name=_("Question"),
        related_name="plugin_question_placeholders",
    )
    slug = models.SlugField(
        null=True,
        blank=True,
        verbose_name=_("Placeholder name"),
        help_text=_(
            "By default, the placeholder will look like {question_123}, but you can change it to {question_something_else}"
        ),
    )
    fallback_content = I18nTextField(
        null=True,
        blank=True,
        verbose_name=_("Fallback"),
        help_text=_("Will be used when no other condition matches. Can be empty."),
    )
    use_fallback_when_unanswered = models.BooleanField(
        default=False,
        verbose_name=_("Use fallback when the question was not answered"),
        help_text=_(
            "Usually, the fallback will only be used when the question has been answered, but in a way that none "
            "of your rules cover. Turn on if you always want to use the fallback, even when the question has not been "
            "answered at all."
        ),
    )

    objects = ScopedManager(organizer="question__event__organizer")

    @property
    def placeholder_name(self):
        return self.slug or self.question_id

    def render(self, order):
        from pretix.base.models.orders import QuestionAnswer

        matches = {}  # We use the fact that dicts are ordered now
        any_unanswered = False

        for position in order.positions.all():
            answer = QuestionAnswer.objects.filter(
                orderposition=position, question=self.question
            ).first()
            if answer:
                match = None
                for rule in self.rules.all():
                    if rule.matches(answer):
                        match = rule
                        break  # Only the first matching rule is used, for each orderposition.
                matches[match or "fallback"] = True
            else:
                any_unanswered = True

        use_fallback = matches.pop("fallback", False) or (
            any_unanswered and self.use_fallback_when_unanswered
        )
        matches = sorted(list(matches.keys()), key=lambda r: r.position)
        content = [match.content for match in matches]
        if use_fallback:
            content.append(self.fallback_content)
        return "\n\n".join([str(c) for c in content])


class PlaceholderRule(models.Model):
    class ComparisonOperation(models.TextChoices):
        EQUALS = "eq", _("Equal to")
        IEQUALS = "ieq", _("Equal to (case insensitive)")
        LESS_THAN = "lt", _("Less than / earlier than")
        LESS_OR_EQUAL_THAN = "lte", _("Less or same as / earlier or same as")
        MORE_THAN = "gt", _("Greater than / later than")
        MORE_OR_EQUAL_THAN = "gte", _("Greater or same as / later or same as")
        IS_TRUE = "bool", _("Is true / has been answered")

    placeholder = models.ForeignKey(
        QuestionPlaceholder, on_delete=models.CASCADE, related_name="rules"
    )

    content = I18nTextField(
        null=True,
        blank=True,
        verbose_name=_("Content"),
        help_text=_("Will be inserted into the email if the condition matches."),
    )
    condition_content = models.TextField(null=True, blank=True)
    condition_operation = models.CharField(
        max_length=4, choices=ComparisonOperation.choices
    )
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ("position", "id")

    @cached_property
    def question_type(self):
        return self.placeholder.question.type

    @cached_property
    def value(self):
        return self.placeholder.question.clean_answer(self.condition_content)

    @classmethod
    def get_allowed_methods(cls, question_type):
        global_methods = [cls.ComparisonOperation.IS_TRUE]
        true_ish_methods = global_methods + [cls.ComparisonOperation.EQUALS]

        comparison_methods = global_methods + [
            cls.ComparisonOperation.EQUALS,
            cls.ComparisonOperation.LESS_THAN,
            cls.ComparisonOperation.LESS_OR_EQUAL_THAN,
            cls.ComparisonOperation.MORE_THAN,
            cls.ComparisonOperation.MORE_OR_EQUAL_THAN,
        ]

        text_methods = [cls.ComparisonOperation.IEQUALS]

        methods = {
            Question.TYPE_BOOLEAN: true_ish_methods,
            Question.TYPE_FILE: global_methods,
            Question.TYPE_DATE: comparison_methods,
            Question.TYPE_DATETIME: comparison_methods,
            Question.TYPE_TIME: comparison_methods,
            Question.TYPE_NUMBER: comparison_methods,
            Question.TYPE_PHONENUMBER: true_ish_methods,
            Question.TYPE_STRING: comparison_methods + text_methods,
            Question.TYPE_TEXT: comparison_methods + text_methods,
            Question.TYPE_COUNTRYCODE: comparison_methods,
            Question.TYPE_CHOICE: true_ish_methods,
            # Question.TYPE_CHOICE_MULTIPLE: comparison_methods,
        }
        return set(methods[question_type])

    @cached_property
    def allowed_methods(self):
        return self.get_allowed_methods(self.question_type)

    @cached_property
    def comparison_method(self):
        methods = {
            self.ComparisonOperation.EQUALS: self._compare_equals,
            self.ComparisonOperation.IEQUALS: self._compare_iequals,
            self.ComparisonOperation.LESS_THAN: self._compare_less_than,
            self.ComparisonOperation.LESS_OR_EQUAL_THAN: self._compare_less_or_equal_than,
            self.ComparisonOperation.MORE_THAN: self._compare_more_than,
            self.ComparisonOperation.MORE_OR_EQUAL_THAN: self._compare_more_or_equal_than,
            self.ComparisonOperation.IS_TRUE: self._compare_boolean,
        }
        return methods[self.condition_operation]

    def _compare_boolean(self, value):
        return bool(value)

    def _compare_equals(self, value):
        return value == self.value

    def _compare_iequals(self, value):
        return str(value).lower() == str(self.value).lower()

    def _compare_less_than(self, value):
        return value < self.value

    def _compare_less_or_equal_than(self, value):
        return value <= self.value

    def _compare_more_than(self, value):
        return value > self.value

    def _compare_more_or_equal_than(self, value):
        return value >= self.value

    def matches(self, answer):
        try:
            if answer.question.type == Question.TYPE_CHOICE:
                answer_value = answer.question.clean_answer(answer.options.first())
            else:
                answer_value = answer.question.clean_answer(answer.answer)
        except Exception as e:
            warnings.warn(f"Error parsing answer value: {e}")
            return False

        try:
            return bool(self.comparison_method(answer_value))
        except Exception as e:
            warnings.warn(
                f"Error when comparing values {self.value} and {answer_value}: {e}"
            )
