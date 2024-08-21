import questionary


class PromptView:
    """
    Classe pour gérer les dialogues de saisie et de sélection utilisateur.
    """

    @classmethod
    def prompt_confirm_statut(cls, **kwargs):
        """
        Demande une confirmation pour sélectionner un statut.

        Args:
            **kwargs: Arguments supplémentaires pour la fonction `questionary.confirm`.

        Returns:
            bool: `True` si l'utilisateur confirme, sinon `False`.
        """
        return questionary.confirm(
            "Souhaitez-vous sélectionner un statut ?", **kwargs).ask()

    @classmethod
    def prompt_select(cls, text, choice, **kwargs):
        """
        Affiche une liste de choix pour que l'utilisateur en sélectionne un.

        Args:
            text (str): Question ou texte affiché pour l'utilisateur.
            choice (list): Liste des choix disponibles.
            **kwargs: Arguments supplémentaires pour la fonction `questionary.select`.

        Returns:
            str: Choix sélectionné par l'utilisateur.

        Raises:
            KeyboardInterrupt: Si l'utilisateur interrompt la sélection.
        """
        result = questionary.select(
            text, choices=choice, **kwargs
        ).ask()
        if result is None:
            raise KeyboardInterrupt
        return result
