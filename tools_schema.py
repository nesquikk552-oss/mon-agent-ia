TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "lire_fichier",
            "description": "Lit le contenu d'un fichier texte",
            "parameters": {
                "type": "object",
                "properties": {"chemin": {"type": "string"}},
                "required": ["chemin"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ecrire_fichier",
            "description": "Écrit du contenu dans un fichier (le crée s'il n'existe pas)",
            "parameters": {
                "type": "object",
                "properties": {
                    "chemin": {"type": "string"},
                    "contenu": {"type": "string"}
                },
                "required": ["chemin", "contenu"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lister_fichiers",
            "description": "Liste les fichiers d'un dossier",
            "parameters": {
                "type": "object",
                "properties": {"dossier": {"type": "string"}},
                "required": []
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "calculer",
            "description": "Calcule une expression mathématique simple",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"]
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "ajouter_a_memoire",
            "description": "Sauvegarde une information importante sur l'utilisateur, classée par catégorie",
            "parameters": {
                "type": "object",
                "properties": {
                    "information": {"type": "string"},
                    "categorie": {
                        "type": "string",
                        "description": "Catégorie de l'information : etudes, preferences, taches, ou general"
                    }
                },
                "required": ["information"]
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "rechercher_web",
            "description": "Cherche des informations actuelles sur internet",
            "parameters": {
                "type": "object",
                "properties": {"requete": {"type": "string"}},
                "required": ["requete"]
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "obtenir_date_heure",
            "description": "Donne la date et l'heure actuelles",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "creer_flashcard",
            "description": "Crée une flashcard de révision avec une question et sa réponse",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "reponse": {"type": "string"}
                },
                "required": ["question", "reponse"]
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "convertir_unite",
            "description": "Convertit une valeur d'une unité à une autre",
            "parameters": {
                "type": "object",
                "properties": {
                    "valeur": {"type": "number"},
                    "de_unite": {"type": "string"},
                    "vers_unite": {"type": "string"}
                },
                "required": ["valeur", "de_unite", "vers_unite"]
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "compter_mots",
            "description": "Compte le nombre de mots et de caractères d'un texte",
            "parameters": {
                "type": "object",
                "properties": {"texte": {"type": "string"}},
                "required": ["texte"]
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "obtenir_meteo",
            "description": "Donne la météo actuelle d'une ville",
            "parameters": {
                "type": "object",
                "properties": {"ville": {"type": "string"}},
                "required": ["ville"]
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "envoyer_email",
            "description": "Envoie un email à un destinataire",
            "parameters": {
                "type": "object",
                "properties": {
                    "destinataire": {"type": "string"},
                    "sujet": {"type": "string"},
                    "message": {"type": "string"}
                },
                "required": ["destinataire", "sujet", "message"]
            }
        }
    },
{
        "type": "function",
        "function": {
            "name": "resumer_memoire",
            "description": "Affiche un résumé de tout ce qui est mémorisé sur l'utilisateur",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
{
        "type": "function",
        "function": {
            "name": "creer_skill",
            "description": "Crée un nouveau mode de comportement (skill) personnalisé",
            "parameters": {
                "type": "object",
                "properties": {
                    "nom": {"type": "string"},
                    "contenu": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["nom", "contenu", "description"]
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "lire_pdf",
            "description": "Lit le contenu d'un fichier PDF",
            "parameters": {
                "type": "object",
                "properties": {"chemin": {"type": "string"}},
                "required": ["chemin"]
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "suivre_progression",
            "description": "Enregistre l'avancement de révision d'une matière",
            "parameters": {
                "type": "object",
                "properties": {
                    "matiere": {"type": "string"},
                    "statut": {"type": "string"}
                },
                "required": ["matiere", "statut"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "voir_progression",
            "description": "Affiche l'historique de progression des révisions",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "exporter_donnees",
            "description": "Crée une sauvegarde de toutes les données importantes (mémoire, progression, flashcards)",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "planifier_revisions",
            "description": "Crée un planning de révision réparti jusqu'à une date d'examen donnée",
            "parameters": {
                "type": "object",
                "properties": {
                    "sujets": {"type": "string", "description": "Liste des sujets séparés par des virgules"},
                    "date_examen": {"type": "string", "description": "Date de l'examen au format AAAA-MM-JJ"}
                },
                "required": ["sujets", "date_examen"]
            }
        }
    },
{
        "type": "function",
        "function": {
            "name": "rechercher_avec_alpha",
            "description": "Délègue une recherche approfondie à Alpha, un agent de recherche spécialisé qui explore le web et renvoie une synthèse claire et sourcée. À utiliser de préférence à rechercher_web pour les questions qui demandent une vraie synthèse (sujets complexes, comparaisons, questions d'actualité détaillées) plutôt qu'un simple résultat brut.",
            "parameters": {
                "type": "object",
                "properties": {"question": {"type": "string"}},
                "required": ["question"]
            }
        }
    }
    ,{
        "type": "function",
        "function": {
            "name": "gerer_fichiers_avec_beta",
            "description": "Délègue une tâche de gestion de fichiers à Beta, un agent spécialisé qui peut lire, écrire, lister des fichiers et compter des mots, en enchaînant plusieurs opérations si nécessaire. À utiliser pour les demandes qui impliquent plusieurs étapes sur des fichiers (ex: comparer deux fichiers, résumer le contenu de plusieurs fichiers, lister puis analyser).",
            "parameters": {
                "type": "object",
                "properties": {"instruction": {"type": "string"}},
                "required": ["instruction"]
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "resoudre_avec_grio",
            "description": "Délègue une tâche mathématique à Grio, un agent spécialisé en calculs, conversions d'unités et mathématiques (simples, fines ou appliquées), qui vérifie et corrige lui-même ses résultats avant de répondre. À utiliser pour toute demande mathématique substantielle plutôt que l'outil calculer seul.",
            "parameters": {
                "type": "object",
                "properties": {"instruction": {"type": "string"}},
                "required": ["instruction"]
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "gerer_revisions_avec_delta",
            "description": "Délègue une tâche de révision à Delta, un agent spécialisé qui crée des flashcards, suit et consulte la progression, planifie les révisions jusqu'à une date d'examen, et génère des QCM. À utiliser pour toute demande liée aux révisions plutôt que les outils individuels.",
            "parameters": {
                "type": "object",
                "properties": {"instruction": {"type": "string"}},
                "required": ["instruction"]
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "gerer_agenda_temps_avec_gamma",
            "description": "Délègue une tâche à Gamma, un agent spécialisé qui gère l'agenda (ajout, liste, suppression d'événements), donne la date et l'heure dans n'importe quel fuseau horaire, et la météo n'importe où dans le monde. À utiliser pour toute demande liée à l'agenda, aux fuseaux horaires ou à la météo.",
            "parameters": {
                "type": "object",
                "properties": {"instruction": {"type": "string"}},
                "required": ["instruction"]
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "gerer_documents_avec_lambda",
            "description": "Délègue une tâche à Lambda, un agent spécialisé dans la gestion de documents : lecture et création de fichiers Word, Excel, PowerPoint et PDF. À utiliser pour toute demande impliquant ces types de fichiers.",
            "parameters": {
                "type": "object",
                "properties": {"instruction": {"type": "string"}},
                "required": ["instruction"]
            }
        }
    }
]