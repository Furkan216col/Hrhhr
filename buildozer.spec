[app]
title = J.A.R.V.I.S Android
package.name = jarvisassistant
package.domain = com.enes
source.dir = .
source.include_exts = py,json,txt,png,jpg,kv
version = 4.6.2
requirements = python3,kivy,requests,pyjnius
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 35
android.minapi = 23
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
