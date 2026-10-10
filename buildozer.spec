[app]

title = FluGenerator
package.name = flugenerator
package.domain = org.flugenerator
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,atlas
version = 1.0.0
requirements = python3,kivy==2.3.1
orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 23
android.ndk = 25b
android.sdk = 33
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = False
android.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1