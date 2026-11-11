#!/usr/bin/env bash
# Builds a signed APK of the UniqNextGen Estimate Builder without Gradle.
# Usage (Git Bash):  bash android-app/build.sh
# Needs: JDK 17 and Android SDK (build-tools 34.0.0, platforms;android-34) under $TOOLS.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
TOOLS="${TOOLS:-/c/Users/Kiruthika/android-build}"
JAVA_HOME="${JAVA_HOME:-$(ls -d "$TOOLS"/jdk-17* | head -1)}"
SDK="$TOOLS/sdk"
BT="$SDK/build-tools/34.0.0"
ANDROID_JAR="$SDK/platforms/android-34/android.jar"
JAVA="$JAVA_HOME/bin/java"; JAVAC="$JAVA_HOME/bin/javac"; KEYTOOL="$JAVA_HOME/bin/keytool"
VERSION_CODE="${VERSION_CODE:-1}"; VERSION_NAME="${VERSION_NAME:-1.0}"

OUT="$HERE/build"; rm -rf "$OUT"; mkdir -p "$OUT/res" "$OUT/gen" "$OUT/classes" "$OUT/dex"

echo "1/7  Copying web app into assets"
cp "$ROOT/web/index.html" "$HERE/assets/index.html"
# use the bundled jsPDF so the app works offline
sed -i 's#https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js#jspdf.umd.min.js#' "$HERE/assets/index.html"
grep -q 'src="jspdf.umd.min.js"' "$HERE/assets/index.html"

echo "2/7  Compiling resources"
"$BT/aapt2.exe" compile --dir "$HERE/res" -o "$OUT/res.zip"

echo "3/7  Linking manifest, resources and assets"
"$BT/aapt2.exe" link -o "$OUT/base.apk" -I "$ANDROID_JAR" \
  --manifest "$HERE/AndroidManifest.xml" -A "$HERE/assets" --java "$OUT/gen" \
  --min-sdk-version 24 --target-sdk-version 34 \
  --version-code "$VERSION_CODE" --version-name "$VERSION_NAME" "$OUT/res.zip"

echo "4/7  Compiling Java"
"$JAVAC" -source 8 -target 8 -bootclasspath "$ANDROID_JAR" -Xlint:-options -encoding UTF-8 \
  -d "$OUT/classes" $(find "$HERE/src" "$OUT/gen" -name '*.java')

echo "5/7  Converting to dex"
"$JAVA" -cp "$BT/lib/d8.jar" com.android.tools.r8.D8 --release --min-api 24 \
  --lib "$ANDROID_JAR" --output "$OUT/dex" $(find "$OUT/classes" -name '*.class')
cp "$OUT/base.apk" "$OUT/unsigned.apk"
python -c "import zipfile,sys; z=zipfile.ZipFile(sys.argv[1],'a',zipfile.ZIP_DEFLATED); z.write(sys.argv[2],'classes.dex'); z.close()" \
  "$(cygpath -w "$OUT/unsigned.apk")" "$(cygpath -w "$OUT/dex/classes.dex")"

echo "6/7  Aligning"
"$BT/zipalign.exe" -f -p 4 "$OUT/unsigned.apk" "$OUT/aligned.apk"

echo "7/7  Signing"
KS_DIR="$HERE/keystore"; KS="$KS_DIR/uniqnextgen-release.jks"; PROPS="$KS_DIR/keystore.properties"
mkdir -p "$KS_DIR"
if [ ! -f "$KS" ]; then
  PASS="$(python -c 'import secrets;print(secrets.token_urlsafe(18))')"
  printf 'storeFile=uniqnextgen-release.jks\nkeyAlias=uniqnextgen\nstorePassword=%s\n' "$PASS" > "$PROPS"
  "$KEYTOOL" -genkeypair -keystore "$KS" -storetype PKCS12 -alias uniqnextgen -keyalg RSA -keysize 2048 \
    -validity 10000 -storepass "$PASS" -keypass "$PASS" \
    -dname "CN=UniqNextGen, OU=Uniq Technologies, O=UniqNextGen, C=IN" >/dev/null
  echo "     Created signing key: $KS (password in keystore.properties - back both up!)"
fi
PASS="$(grep '^storePassword=' "$PROPS" | cut -d= -f2-)"
mkdir -p "$ROOT/releases"; FINAL="$ROOT/releases/UniqNextGen-Estimates-v$VERSION_NAME.apk"
"$JAVA" -jar "$BT/lib/apksigner.jar" sign --ks "$KS" --ks-key-alias uniqnextgen \
  --ks-pass "pass:$PASS" --key-pass "pass:$PASS" --out "$FINAL" "$OUT/aligned.apk"
"$JAVA" -jar "$BT/lib/apksigner.jar" verify "$FINAL"
echo "Done: $FINAL ($(du -h "$FINAL" | cut -f1))"
