(function ($, Drupal, drupalSettings) {
  window.tarteaucitronForceExpire = '180';

  const uriKnowMore = drupalSettings.saclay_tarteaucitron.uriKnowMore;
  window.tarteaucitronForceLanguage = drupalSettings.path.currentLanguage;

  if (drupalSettings.path.currentLanguage == 'fr') {
    window.tarteaucitronCustomText = {
      "mandatoryTitle": "Cookies obligatoires",
      "mandatoryText": "Ces cookies sont strictement obligatoires au bon fonctionnement du site. Ces cookies incluent les cookies qui nous permettent de conserver vos choix concernant le dépôt de cookies. Cette finalité est requise par notre site pour fonctionner normalement et ne peut pas être désactivée.",
      "alertBigPrivacy": "Ce site utilise des cookies pour le bon fonctionnement du site et l’expérience utilisateur : lecture de vidéos, partage du contenu sur les réseaux sociaux, cartes géographiques interactives, mesure de l’audience des pages. Les cookies nécessaires sont ceux liés au fonctionnement de l'espace connecté et de la barre de notification qui peut être utilisée sur le site. L’Université Paris-Saclay est responsable du traitement des données. Vous pouvez accepter ou refuser l’ensemble des cookies ou personnaliser votre choix. En autorisant les services tiers, vous acceptez le dépôt et la lecture de cookies et l'utilisation de technologies de suivi nécessaires à leur bon fonctionnement. Les données sont conservées pendant 13 mois maximum. Vous pourrez à tout moment revoir vos choix en cliquant sur le lien « Gestion des cookies » qui se trouve dans le pied de page du site.<br/><a href='https://www.universite-paris-saclay.fr/politique-des-cookies'>Politique de gestion des cookies</a>",
      "disclaimer": "En autorisant ces services tiers, vous acceptez le dépôt et la lecture de cookies et l'utilisation de technologies de suivi nécessaires à leur bon fonctionnement.<br/>" +
        "Pour en savoir plus sur les données collectées et leur utilisation, <a href='" + uriKnowMore + "'>consultez les informations sur les cookies</a>.",
      // "alertSmall": "Paramètres des cookies",
      // "personalize": "Paramètres des cookies",
      // "acceptAll": "Oui, je suis d'accord",
      // "denyAll": "Tout refuser",
      // "allowAll": "Tout Autoriser",
      // "privacyUrl": "Plus d'infos",
      // "all": "Préférences",
      // "allow": "Autoriser",
      // "deny": "Refuser",
      // "allowed": "Actif",
      // "disallowed": "Inactif",
      // "more": "Plus d'infos",
      // "source": "Voir le site officiel",
    };
  }
  else if (drupalSettings.path.currentLanguage == 'en') {
    window.tarteaucitronCustomText = {
      "mandatoryText": "This website uses cookies necessary for its proper functioning which cannot be deactivated. These cookies include those that enable us to keep track of your choices concerning the deposit of cookies.",
      "disclaimer": "By allowing these third party services, you accept their cookies and the use of tracking technologies necessary for their proper functioning.<br/>" +
        "To learn more about the data collected and its use, <a href='" + uriKnowMore + "'>see the information on cookies</a>.",
    }
  }
})(jQuery, Drupal, drupalSettings);
