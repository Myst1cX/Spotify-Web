# Spotify-Web
A wrapper around the Spotify website

## Third-party software
See [THIRD_PARTY_NOTICES.txt](THIRD_PARTY_NOTICES.txt) (a copy is also bundled inside the app's assets folder).

The custom WebView engine is built on [WebViewUpgrade](https://github.com/JonaNorman/WebViewUpgrade) by JonaNorman (Apache License 2.0).

The Eruda Console switch in Settings uses [Eruda](https://github.com/liriliri/eruda) by liriliri (MIT License). The library file, eruda.js, is bundled in the app's assets folder.

Debug Logging and the Logger are adapted from Spotilol by lyssadev (`lyssadev/Spotilol`, repository currently unavailable). The app's toast styling and animations (pill shape, Dark colours, entrance, swipe and exit) come from the Spotifuck Mobile userscript, which adapts Spotilol's ToastFix.

The Musixmatch lyrics lookup through the signed-in web api (Web Lyrics+ userscript, from 17.68+ onwards) is adapted from the pull request `fix/musixmatch-signed-web-api` by zensu357 to [bettergnome-lyricsbar](https://github.com/zensu357/bettergnome-lyricsbar/tree/fix/musixmatch-signed-web-api) (MIT License).
