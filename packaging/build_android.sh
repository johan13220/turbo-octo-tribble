#!/bin/bash
# Build SEO Dashboard Android APK using Buildozer.
# Run on Ubuntu 20.04+ (x86_64). The first build downloads Android SDK/NDK
# (~1.5 GB) and can take 20–40 minutes. Subsequent builds are much faster.
set -euo pipefail

log() { echo "[android] $*"; }
die() { echo "[error] $*" >&2; exit 1; }

# ── Prerequisites ─────────────────────────────────────────────────────────────
REQUIRED_PKGS="python3-pip python3-venv git zip unzip openjdk-17-jdk"
log "Checking system packages: $REQUIRED_PKGS"
for pkg in $REQUIRED_PKGS; do
    dpkg -s "$pkg" >/dev/null 2>&1 || {
        log "Installing $pkg..."
        sudo apt-get install -y "$pkg"
    }
done

# ── Buildozer ─────────────────────────────────────────────────────────────────
if ! command -v buildozer >/dev/null 2>&1; then
    log "Installing buildozer + cython..."
    pip install --quiet buildozer cython
fi

# ── APK icon: convert SVG → PNG if needed ─────────────────────────────────────
ICON_PNG="packaging/seo-dashboard.png"
if [ ! -f "$ICON_PNG" ]; then
    if command -v rsvg-convert >/dev/null 2>&1; then
        rsvg-convert -w 512 -h 512 packaging/seo-dashboard.svg -o "$ICON_PNG"
        log "Icon converted: $ICON_PNG"
    elif command -v inkscape >/dev/null 2>&1; then
        inkscape --export-png="$ICON_PNG" -w 512 -h 512 packaging/seo-dashboard.svg
        log "Icon converted: $ICON_PNG"
    else
        log "Warning: rsvg-convert/inkscape not found — APK will use default icon."
        log "Install with: sudo apt install librsvg2-bin"
    fi
fi

# ── Build ─────────────────────────────────────────────────────────────────────
BUILD_TYPE="${1:-debug}"

if [ "$BUILD_TYPE" = "release" ]; then
    log "Building release APK..."
    buildozer android release
    APK_PATH=$(find .buildozer/android/platform/build-*/dists/seodashboard/bin/ \
                   -name "*.apk" -newer buildozer.spec 2>/dev/null | head -1)
else
    log "Building debug APK (use 'bash packaging/build_android.sh release' for release)..."
    buildozer android debug
    APK_PATH=$(find .buildozer/android/platform/build-*/dists/seodashboard/bin/ \
                   -name "*debug*.apk" 2>/dev/null | head -1)
fi

if [ -n "$APK_PATH" ] && [ -f "$APK_PATH" ]; then
    DEST="SEODashboard-${BUILD_TYPE}.apk"
    cp "$APK_PATH" "$DEST"
    log ""
    log "Done: $DEST  ($(du -sh "$DEST" | cut -f1))"
    log ""
    log "Install on device:  adb install -r $DEST"
    log "Install via cable:  adb install $DEST"
else
    log "APK built — check .buildozer/android/platform/build-*/dists/seodashboard/bin/"
fi
