from pretix.base.email import BaseMailTextPlaceholder


class QuestionMailPlaceholder(BaseMailTextPlaceholder):
    def __init__(self, placeholder):
        self._identifier = f"question_{placeholder.placeholder_name}"
        self.placeholder = placeholder

    @property
    def required_context(self):
        return ["order"]

    @property
    def identifier(self):
        return self._identifier

    def render(self, context):
        return self.placeholder.render(context["order"])

    def render_sample(self, context):
        return self.placeholder.fallback_content
