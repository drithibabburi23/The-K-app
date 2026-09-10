#!/usr/bin/env bash

set -euo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repository_root"

if [[ -f pubspec.yaml ]]; then
  flutter_project="."
elif [[ -f karigar_connect/pubspec.yaml ]]; then
  flutter_project="karigar_connect"
else
  echo "No Flutter project was found; publishing the documentation landing page."
  rm -rf build/web
  mkdir -p build/web
  cp -R public/. build/web/
  exit 0
fi

if ! command -v flutter >/dev/null 2>&1; then
  flutter_home="${FLUTTER_HOME:-$HOME/.cache/flutter}"

  if [[ ! -x "$flutter_home/bin/flutter" ]]; then
    rm -rf "$flutter_home"
    git clone --depth 1 --branch stable https://github.com/flutter/flutter.git "$flutter_home"
  fi

  export PATH="$flutter_home/bin:$PATH"
fi

(
  cd "$flutter_project"
  flutter config --enable-web
  flutter pub get
  flutter build web --release
)

if [[ "$flutter_project" != "." ]]; then
  rm -rf build/web
  mkdir -p build
  cp -R "$flutter_project/build/web" build/web
fi
