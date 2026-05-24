[app]
title = SEO Dashboard
package.name = seodashboard
package.domain = com.seodashboard

# Entry point is android_app.py (not app.py which is Streamlit)
source.dir = .
source.include_exts = py,png,jpg,svg,kv,atlas,j2,example
source.include_patterns = .env.example,reports/templates/*
source.exclude_dirs = build,dist,.venv,venv,tests,__pycache__,packaging,.git,squashfs-root
source.exclude_patterns = *.AppImage,app.py

version = 1.0.0

# ─── Python requirements ────────────────────────────────────────────────────
# pydantic: python-for-android ships a recipe for pydantic v1 (pure Python).
# If the p4a recipe is unavailable in your version, pin to pydantic==1.10.21.
# pydantic-settings is NOT included — android_compat/config.py replaces it.
# httpx requires h11 + sniffio + anyio + certifi (all pure Python).
requirements = python3,kivy==2.3.0,kivymd==1.2.0,requests,httpx,h11,sniffio,anyio,certifi,charset-normalizer,urllib3,idna,exceptiongroup,beautifulsoup4,soupsieve,python-dotenv,diskcache,pillow,pydantic

# ─── Android settings ────────────────────────────────────────────────────────
android.permissions = INTERNET
android.api = 33
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24

# Build for 64-bit ARM (modern devices). Add armeabi-v7a for older devices.
android.arch = arm64-v8a

# ─── App metadata ────────────────────────────────────────────────────────────
orientation = portrait
fullscreen = 0
icon.filename = packaging/seo-dashboard.png

# Splash screen (optional — remove if no image available)
# presplash.filename = %(source.dir)s/packaging/splash.png

# ─── Build ────────────────────────────────────────────────────────────────────
log_level = 2
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
