(function ($, Drupal, drupalSettings) {

  Drupal.behaviors.saclay_tarteaucitron = {
    attach: function (context, settings) {

      let params = {
        "privacyUrl": "",
        "hashtag": "#rgpd",
        "cookieName": "saclay-tac",
        "orientation": "bottom",
        "showAlertSmall": false,
        "cookieslist": false,
        "showIcon": false,
        "iconPosition": "BottomRight",
        "adblocker": false,
        "DenyAllCta": true,
        "AcceptAllCta": true,
        "highPrivacy": true,
        "handleBrowserDNTRequest": false,
        "removeCredit": true,
        "moreInfoLink": true,
        "useExternalCss": false,
        "mandatory": true,
        "reloadThePage": true,
      };

      if (settings.cookieDomain) {
        params.cookieDomain = settings.cookieDomain;
      }

      tarteaucitron.init(params);

      if (settings.saclay_rgpd.matomo_key !== undefined) {
        tarteaucitron.user.matomoHost = settings.saclay_rgpd.matomo_host;
        tarteaucitron.user.matomoId = settings.saclay_rgpd.matomo_key;
        (tarteaucitron.job = tarteaucitron.job || []).push('matomo');
      }

      (tarteaucitron.job = tarteaucitron.job || []).push('x_social_wall');
      (tarteaucitron.job = tarteaucitron.job || []).push('fb_social_wall');
      (tarteaucitron.job = tarteaucitron.job || []).push('youtube_saclay');
      (tarteaucitron.job = tarteaucitron.job || []).push('dailymotion');
      (tarteaucitron.job = tarteaucitron.job || []).push('vimeo');
      (tarteaucitron.job = tarteaucitron.job || []).push('saclay_openstreetmap');
      (tarteaucitron.job = tarteaucitron.job || []).push('maps_noapi');

      $('a.tarteaucitron.openpanel').on('click', function() {
        tarteaucitron.userInterface.openPanel();
      });
    }
  };

})(jQuery, Drupal, drupalSettings);
