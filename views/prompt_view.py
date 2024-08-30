import questionary


class PromptView:
    """
    Classe pour gérer les dialogues de saisie et de sélection utilisateur.
    """

    @classmethod
    def prompt_select(cls, text, choice, **kwargs):
        """
        Affiche une liste de choix et demande à l'utilisateur de sélectionner une option.

        Paramètres :
        ------------
        text (str) : Question ou texte affiché pour l'utilisateur.
        choice (list) : Liste des choix disponibles.
        **kwargs : Arguments supplémentaires pour la fonction `questionary.select`.

        Retourne :
        -----------
        str : Choix sélectionné par l'utilisateur.

        Lève :
        -------
        KeyboardInterrupt : Si l'utilisateur interrompt la sélection.
        """
        result = questionary.select(
            text, choices=choice, **kwargs
        ).ask()
        if result is None:
            raise KeyboardInterrupt
        return result
