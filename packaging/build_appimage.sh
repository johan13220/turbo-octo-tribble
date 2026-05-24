#!/bin/bash
# Build script for SEO Dashboard AppImage
# Requirements: wget, curl (standard on Ubuntu)
# Output: SEODashboard-<version>-x86_64.AppImage
set -euo pipefail

APP_NAME="SEODashboard"
APP_VERSION="${VERSION:-1.0.0}"
ARCH="x86_64"
PYTHON_VERSION="3.11"
PYTHON_VER_NODOT="311"
BUILD_DIR="build"
APPDIR="${BUILD_DIR}/${APP_NAME}.AppDir"

APPIMAGETOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
PYTHON_APPIMAGE_URL="https://github.com/niess/python-appimage/releases/download/python${PYTHON_VERSION}/python${PYTHON_VERSION}-cp${PYTHON_VER_NODOT}-cp${PYTHON_VER_NODOT}-manylinux2014_${ARCH}.AppImage"

log() { echo "[build] $*"; }
die() { echo "[error] $*" >&2; exit 1; }

# --- Prerequisites ---
command -v wget >/dev/null 2>&1 || die "wget is required: sudo apt install wget"
command -v curl >/dev/null 2>&1 || die "curl is required: sudo apt install curl"

log "Building ${APP_NAME} v${APP_VERSION} for ${ARCH}"

# --- Clean AppDir, keep cached downloads ---
rm -rf "$APPDIR"
mkdir -p "$BUILD_DIR"

# --- Download appimagetool (cached) ---
APPIMAGETOOL="${BUILD_DIR}/appimagetool-${ARCH}"
if [ ! -f "$APPIMAGETOOL" ]; then
    log "Downloading appimagetool..."
    wget -q --show-progress -O "$APPIMAGETOOL" "$APPIMAGETOOL_URL"
    chmod +x "$APPIMAGETOOL"
fi

# --- Download Python AppImage (cached, ~50 MB) ---
PYTHON_APPIMAGE="${BUILD_DIR}/python${PYTHON_VERSION}-${ARCH}.AppImage"
if [ ! -f "$PYTHON_APPIMAGE" ]; then
    log "Downloading Python ${PYTHON_VERSION} AppImage (50 MB, cached after first run)..."
    wget -q --show-progress -O "$PYTHON_APPIMAGE" "$PYTHON_APPIMAGE_URL"
    chmod +x "$PYTHON_APPIMAGE"
fi

# --- Extract Python AppImage as AppDir base ---
log "Extracting Python AppImage..."
cd "$BUILD_DIR"
"./${PYTHON_APPIMAGE##*/}" --appimage-extract >/dev/null
mv squashfs-root "${APP_NAME}.AppDir"
cd ..

# --- Install Python dependencies into AppDir ---
log "Installing Python dependencies (this may take a few minutes)..."
PYTHON_BIN="${APPDIR}/usr/bin/python${PYTHON_VERSION}"
"$PYTHON_BIN" -m pip install \
    --quiet \
    --no-warn-script-location \
    -r requirements.txt

# weasyprint needs system libs (libpango, libcairo) that are not bundled.
# PDF export will be gracefully disabled at runtime — this is expected.

# --- Bundle application source ---
log "Bundling application files..."
mkdir -p "${APPDIR}/app"
cp app.py "${APPDIR}/app/"
cp .env.example "${APPDIR}/app/.env.example"
for d in core providers analysis ui reports; do
    cp -r "$d" "${APPDIR}/app/$d"
done

# --- AppRun, desktop, icon ---
cp packaging/AppRun "${APPDIR}/AppRun"
chmod +x "${APPDIR}/AppRun"

cp packaging/seo-dashboard.desktop "${APPDIR}/seo-dashboard.desktop"
cp packaging/seo-dashboard.svg "${APPDIR}/seo-dashboard.svg"

# appimagetool expects a .DirIcon symlink at the AppDir root
ln -sf seo-dashboard.svg "${APPDIR}/.DirIcon"

# --- Build final AppImage ---
OUTPUT="${APP_NAME}-${APP_VERSION}-${ARCH}.AppImage"
log "Packing AppImage..."
ARCH="$ARCH" "${BUILD_DIR}/appimagetool-${ARCH}" \
    --comp gzip \
    "$APPDIR" "$OUTPUT" 2>/dev/null

log ""
log "Done: ${OUTPUT}"
log "Usage: chmod +x ${OUTPUT} && ./${OUTPUT}"
