import questionary


class PromptView:

    @classmethod
    def prompt_confirm_statut(cls, **kwargs):
        return questionary.confirm(
            "Souhaitez-vous sélectionner un statut ?", **kwargs).ask()

    @classmethod
    def prompt_select(cls, text, choice, **kwargs):
        result = questionary.select(
            text, choices=choice, **kwargs
        ).ask()
        if result is None:
            raise KeyboardInterrupt
        return result
