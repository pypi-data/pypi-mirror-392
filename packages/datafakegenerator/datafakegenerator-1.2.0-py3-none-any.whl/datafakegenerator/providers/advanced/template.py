from datafakegenerator.providers.base_provider import BaseProvider
import re


class TemplateProvider(BaseProvider):

    def __init__(self, *, blank_percentage: float = 0.0, template: str = '', schema_labels=None, **kwargs):
        super().__init__(blank_percentage=blank_percentage, **kwargs)
        self.template = template
        self.schema_labels = set(schema_labels or [])

    def generate_non_blank(self, row_data: dict = None):
        if not self.template:
            return None

        if not row_data:
            return self.template

        # Normalize template: {{field}} → {field}
        text = re.sub(r"\{\{([^}]+)\}\}", r"{\1}", self.template)

        # Find {field} placeholders AFTER normalization
        placeholders = re.findall(r"\{([^}]+)\}", text)

        for label in placeholders:
            value = row_data.get(label)
            text = text.replace(f"{{{label}}}", str(value))

        return text
