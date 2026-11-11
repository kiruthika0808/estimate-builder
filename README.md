# UniqNextGen Estimate Builder

A single-page app for building school estimates for the **AI & Future-Tech School Curriculum**.
Type the school name, choose the training model, tick the items, press **Generate estimate**,
and download a branded PDF. Every generated estimate is saved so it can be edited later.

- Picks the lowest-priced programme that covers every ticked item and shows the **final amount per student** and the **grand total** (also written out in words, Indian style).
- Optional **Additional Service** with a typed name, charged per student:
  ₹150 up to 1,500 students · ₹135 for 1,501–2,500 · ₹100 above 2,500.
- Optional discount % and GST %.
- PDF estimates carry the UniqNextGen logo, estimate number, date, website and email.
- Works on desktop and phones.

## Folder layout

| Path | What it is |
| --- | --- |
| `web/index.html` | The whole app: HTML, CSS and JavaScript in one file, logo embedded |
| `web/Start Estimate Builder.bat` | Double-click to run the app locally on Windows (needs Python) |
| `android-app/` | Android wrapper that builds an installable APK |
| `vercel.json`, `.vercelignore` | Vercel settings: deploys only `web/` and opens the app at `/` |

## Run locally

```bash
python -m http.server 8080 --directory web
```

Then open http://localhost:8080. Saved estimates are kept in that browser's local storage.

## Deploy to Vercel

Import this repo in Vercel with Framework Preset **Other**, no build command, Root Directory left empty.
A tiny root `index.html` forwards visitors to `web/`, so the site root works on any static host. Saved estimates stay in each visitor's own browser.

## Build the Android APK

Needs JDK 17 and the Android SDK (`build-tools;34.0.0`, `platforms;android-34`). In Git Bash:

```bash
VERSION_CODE=4 VERSION_NAME=1.3 TOOLS=/c/Users/Kiruthika/android-build bash android-app/build.sh
```

The signed APK is written to `releases/`. The first build creates a signing key in `android-app/keystore/`.
**Back that folder up and never commit it.** Every update must be signed with the same key,
or phones will refuse to install it over the old version.
