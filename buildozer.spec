[app]

# (str) Title of your application
title = AnnotateClient

# (str) Package name
package.name = annotateclient

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example
source.dir = .

# (str) Source code where the main.py lives
source.include_exts = py,png,jpg,kv,atlas

# (list) Source files to include (let empty to include all the files)
source.include_patterns = 

# (str) Application versioning
version = 0.1

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,hostpython3,openssl,sqlite3

# (int) Android SDK version to use
android.sdk = 29

# (str) Android build tool version to use
android.build_tools = 29.0.2
# (list) Supported arch are: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = armeabi-v7a, arm64-v8a

# (int) Android API to use
android.api = 31

# (int) Minimum API required
android.minapi = 21

# (int) Android NDK version to use
android.ndk = 25b

# (str) Android API

# (str) Android entry point
android.entrypoint = main.py

# (str) Android permissions
android.permissions = INTERNET

# (list) List of service to declare
# services =

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
services = 

# (bool) Indicate whether the application should be fullscreen or not
fullscreen = 0

# (str) Presplash of the application
presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/data/icon.png
