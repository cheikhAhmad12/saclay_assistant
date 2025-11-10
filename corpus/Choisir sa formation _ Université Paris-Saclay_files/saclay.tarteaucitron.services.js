// youtube.
tarteaucitron.services.youtube_saclay = {
  "key": "youtube_saclay",
  "type": "video",
  "name": "Youtube",
  "uri": "https://policies.google.com/technologies/cookies?hl=fr",
  "readmoreLink": "https://policies.google.com/technologies/cookies?hl=fr",
  "needConsent": true,
  "cookies": ['VISITOR_INFO1_LIVE', 'YSC', 'PREF', 'GEUP', 'CONSENT'],
  "js": function () {

    "use strict";

      (function ($) {
        tarteaucitron.fallback(['youtube_player'], function (x) {

            var frame_title = tarteaucitron.fixSelfXSS(tarteaucitron.getElemAttr(x, "title") || 'Youtube iframe'),
                video_id = tarteaucitron.getElemAttr(x, "videoID"),
                srcdoc = tarteaucitron.getElemAttr(x, "srcdoc"),
                loading = tarteaucitron.getElemAttr(x, "loading"),
                video_width = tarteaucitron.getElemAttr(x, "width"),
                frame_width = 'width=',
                video_height = tarteaucitron.getElemAttr(x, "height"),
                frame_height = 'height=',
                video_frame,
                allowfullscreen = tarteaucitron.getElemAttr(x, "allowfullscreen"),
                attrs = ["theme", "rel", "controls", "showinfo", "autoplay", "mute", "start", "loop", "enablejsapi"],
                params = attrs.filter(function (a) {
                    return tarteaucitron.getElemAttr(x, a) !== null;
                }).map(function (a) {
                    return a + "=" + tarteaucitron.getElemAttr(x, a);
               }).join("&");

            if (tarteaucitron.getElemAttr(x, "loop") == 1) {
               params = params + "&playlist=" + video_id;
            }

            if (video_id === undefined) {
                return "";
            }
            if (video_width !== undefined) {
                frame_width += '"' + video_width + '" ';
            } else {
                frame_width += '"" ';
            }
            if (video_height !== undefined) {
                frame_height += '"' + video_height + '" ';
            } else {
                frame_height += '"" ';
            }

            if (srcdoc !== undefined && srcdoc !== null && srcdoc !== "") {
                srcdoc = 'srcdoc="' + srcdoc + '" ';
            } else {
                srcdoc = '';
            }

            if (loading !== undefined && loading !== null && loading !== "") {
                loading = 'loading ';
            } else {
                loading = '';
            }

            video_frame = '<iframe title="' + frame_title + '" type="text/html" ' + frame_width + frame_height + ' src="//www.youtube-nocookie.com/embed/' + video_id + '?' + params + '"' + (allowfullscreen == '0' ? '' : ' webkitallowfullscreen mozallowfullscreen allowfullscreen') + ' ' + srcdoc + ' ' + loading + '></iframe>';
            return video_frame;
        });

        // Intégration via media--remote-video.html:
        $('.videobox.container').each(function() {
          $(this).find('.youtube_saclay').addClass('videobox__frame');
        });

        if ($('.videobox.container .youtube_saclay').length) {
          tarteaucitron.addScript("https://cdn.plyr.io/3.7.8/plyr.polyfilled.js", 'videobox', function() {
            var players = Plyr.setup('.videobox__frame', {
              iconUrl: "/themes/custom/boots/assets/images/plyr.svg",
              controls: ['play-large', 'play', 'progress', 'current-time', 'mute', 'volume', 'captions', 'settings', 'pip', 'airplay', 'fullscreen'],
              settings: ['captions', 'quality', 'speed', 'loop'],
              captions: { active: false, language: 'auto', update: false }
            });
            // Pause other playing videos
            players.forEach(function (player) {
                player.on('play', function () {
                    const others = players.filter((other) => other !== player);
                    others.forEach(function (other) {
                        other.pause();
                    });
                });
            });
          });
       };

      })(jQuery);
  },
  "fallback": function () {
    "use strict";
    var id = 'youtube_saclay';
    tarteaucitron.fallback(['youtube_player'], function (elem) {
      // elem.style.width = elem.getAttribute('width') + 'px';
      // elem.style.height = elem.getAttribute('height') + 'px';
      return tarteaucitron.engage(id);
    });
  }
};

// Twitter wall
tarteaucitron.services.x_social_wall = {
  "key": "x_social_wall",
  "type": "social",
  "name": "Mur du réseau social twitter",
  "uri": "https://help.twitter.com/fr/rules-and-policies/x-cookies",
  "readmoreLink": "https://help.twitter.com/fr/rules-and-policies/x-cookies",
  "needConsent": true,
  "cookies": ['ct0', 'guest_id', '_twitter_sess', 'att'],
  "js": function () {
      "use strict";
      tarteaucitron.fallback(['x_social_wall'], function (x) {
          var frame =
          '<div class="col-md-4">' +
              '<a class="twitter-timeline" data-height="500" href="https://twitter.com/UnivParisSaclay?ref_src=twsrc%5Etfw">Tweets by UnivParisSaclay</a>' +
          '</div>'
          tarteaucitron.addScript('https://platform.twitter.com/widgets.js');
          return frame;
      });
  },
  "fallback": function () {
      "use strict";
      var id = 'x_social_wall';
      tarteaucitron.fallback(['x_social_wall'], function (elem) {
          elem.style = elem.getAttribute('data-style');
          return tarteaucitron.engage(id);
      });
  }
};

// Facebook wall
tarteaucitron.services.fb_social_wall = {
  "key": "fb_social_wall",
  "type": "social",
  "name": "Mur du réseau social Facebook",
  "uri": "https://www.facebook.com/privacy/policies/cookies/",
  "readmoreLink": "https://www.facebook.com/privacy/policies/cookies/",
  "needConsent": true,
  "cookies": ['wd', 'sb', 'datr'],
  "js": function () {
      "use strict";
      tarteaucitron.fallback(['fb_social_wall'], function (x) {
          var frame =
          '<div class="col-md-4">' +
              '<div id="fb-root"></div>' +
              '<div class="fb-page" data-href="https://www.facebook.com/UParisSaclay/" data-tabs="timeline" data-width=""' +
              'data-height="" data-small-header="false" data-adapt-container-width="true" data-hide-cover="false"' +
              'data-show-facepile="true">' +
              '<blockquote cite="https://www.facebook.com/UParisSaclay/" class="fb-xfbml-parse-ignore"><a' +
              'href="https://www.facebook.com/UParisSaclay/">Université Paris-Saclay</a></blockquote>' +
          '</div>'
          tarteaucitron.addScript('https://connect.facebook.net/fr_FR/sdk.js#xfbml=1&version=v5.0', '', '', '', 'data-pagespeed-no-defer', '');
          return frame;
      });
  },
  "fallback": function () {
      "use strict";
      var id = 'fb_social_wall';
      tarteaucitron.fallback(['fb_social_wall'], function (elem) {
          elem.style = elem.getAttribute('data-style');
          return tarteaucitron.engage(id);
      });
  }
};

// Open Street Map
tarteaucitron.services.saclay_openstreetmap = {
  "key": "saclay_openstreetmap",
  "type": "other",
  "name": "Cartes OpenStreetMap",
  "uri": "https://osmfoundation.org/wiki/Privacy_Policy",
  "readmoreLink": "https://osmfoundation.org/wiki/Privacy_Policy",
  "needConsent": true,
  "cookies": ['_pk_id', '_pk_ref'],
  "js": function () {
      "use strict";
      tarteaucitron.fallback(['saclay_openstreetmap'], function (x) {

        var id = x.getAttribute("id"),
        width = x.getAttribute("width"),
        height = x.getAttribute("height"),
        coordinates = '#' + x.getAttribute("coordinates") ?? '';

        var attributes = {
            scaleControl : x.getAttribute("scaleControl") ?? false,
            miniMap : x.getAttribute("miniMap") ?? false,
            scrollWheelZoom : x.getAttribute("scrollWheelZoom") ?? false,
            allowEdit : x.getAttribute("allowEdit") ?? false,
            moreControl : x.getAttribute("moreControl") ?? false,
            captionBar : x.getAttribute("captionBar") ?? false,
            zoomControl : x.getAttribute("zoomControl") ?? true,
            searchControl : x.getAttribute("searchControl") ?? true,
            tilelayersControl : x.getAttribute("tilelayersControl") ?? null,
            embedControl : x.getAttribute("embedControl") ?? null,
            datalayersControl : x.getAttribute("datalayersControl") ?? null,
            onLoadPanel : x.getAttribute("onLoadPanel") ?? 'databrowser',
        };
        var parameters = '';
        Object.keys(attributes).forEach(function(index) {
          if (parameters === '') {
            parameters += '?' + index + '=' + attributes[index];
          }
          else {
            parameters += '&' + index + '=' + attributes[index];
          }
        });
        var widgetURL = "//umap.openstreetmap.fr/fr/map/" + id + parameters + coordinates;
        var frame = '<p><iframe allowfullscreen="" frameborder="0" width="' + width + '" height="' + height + '" src="' + widgetURL + '"></iframe></p>';
          return frame;
      });
  },
  "fallback": function () {
      "use strict";
      var id = 'saclay_openstreetmap';
      tarteaucitron.fallback(['saclay_openstreetmap'], function (elem) {
          elem.style = elem.getAttribute('data-style');
          return tarteaucitron.engage(id);
      });
  }
};
