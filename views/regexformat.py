regex_email = "^[_A-Za-z0-9-\\+]+(\\.[_A-Za-z0-9-]+)*"
regex_email += "@[A-Za-z0-9-]+(\\.[A-Za-z0-9]+)*(\\.[A-Za-z]{2,})$"

regex_phone = "^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$"

regex_password = r".*"


regexformat = {
    '3cn': (
        r"^[A-Za-z0-9-]+$",
        "Au moins 3 caractères sont requis, alpha ou numérique"),
    'alphanum': (
        r"^[a-zA-Z0-9 ]+$",
        "Seul des caractères alpha sont autorisés"),
    'numposmax': (
        r"(?<!-)\b([1-3]?\d{1,5}|100000)\b",
        "Le montant doit être positif et inférieur à 100 000"
    ),
    'date': (
        r'(\d{2})[/.-](\d{2})[/.-](\d{4})$',
        "format dd/mm/yyyy attendu"
    ),
    'alpha': (
        r"^[a-zA-Z ']+$",
        "Seul des caractères alpha sont autorisés"
    ),
    'alpha_nospace': (
        r"^[a-zA-Z ']+$",
        "Seul des caractères alpha sont autorisés"
    ),
    'email': (regex_email, "Le format de l'email est invalide"),
    'phone': (regex_phone, "Ce n'est pas un numéro de téléphone valide"),
    'password': (regex_password, "Le format du mot de passe est invalide")
}