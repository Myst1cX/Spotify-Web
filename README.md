# Spotify-Web
A wrapper around the Spotify website

## Third-party software
See [THIRD_PARTY_NOTICES.txt](THIRD_PARTY_NOTICES.txt) (a copy is also bundled inside the app's assets folder).

The custom WebView engine is built on [WebViewUpgrade](https://github.com/JonaNorman/WebViewUpgrade) by JonaNorman (Apache License 2.0).

The Eruda Console switch in Settings uses [Eruda](https://github.com/liriliri/eruda) by liriliri (MIT License). The library file, eruda.js, is bundled in the app's assets folder.

Debug Logging and the Logger are adapted from Spotilol by lyssadev (`lyssadev/Spotilol`, repository currently unavailable). The app's toast styling and animations (pill shape, Dark colours, entrance, swipe and exit) come from the Spotifuck Mobile userscript, which adapts Spotilol's ToastFix.

The Musixmatch lyrics lookup through the signed-in web api (Web Lyrics+ userscript, from 17.68+ onwards) is adapted from the pull request `fix/musixmatch-signed-web-api` by zensu357 to [bettergnome-lyricsbar](https://github.com/zensu357/bettergnome-lyricsbar/tree/fix/musixmatch-signed-web-api) (MIT License).

Parts of the ad blocking come from [SpotiDuck](https://github.com/23fpsz/SpotiDuck-Releases) by 23fpsz (GPL-3.0): the ad-ID hook (`ad_state_hook.js`, adapted from Duck's file), the silent audio file (`silent.mp3`), the hosts list handling and built-in ad host set, and the compiled hosts list's sources and format. The media browsing and notification bridge, link handling, login detection and background playback also follow SpotiDuck. The ad markers, the idea of leaving an ad out of the playback state and the idea of playing the next song shortly before a song ends when Spotify's second try leaves no other song to point to, and the way the page's own player is reached for that, follow what [Myspoti](https://github.com/kota-zo/myspoti) (GPL-3.0) documents about Spotify's web player; the code is new. 



