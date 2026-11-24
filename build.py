#!/usr/bin/env python3
"""Builds the installable (PWA) versions of the games for GitHub Pages.

Usage: python3 build.py <version>
Reads the single-file games from src/ (refreshed from ../farol and ../ordago when present)
and writes farol/ and ordago/ folders with index.html, manifest, service worker and icons.
"""
import json, os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
VERSION = sys.argv[1] if len(sys.argv) > 1 else "dev"

GAMES = {
    "farol": {"src": "src/farol.html", "name": "Farol", "desc": "Roguelike de póker con amuletos, pergaminos y licores.",
              "bg": "#1b1140", "theme": "#1b1140"},
    "cripticos": {"src": "src/cripticos.html", "name": "Críptico", "desc": "Crípticos en español con pistas de definición, indicador y letras.",
                  "bg": "#f3ecdf", "theme": "#f3ecdf"},
    "ordago": {"src": "src/ordago.html", "name": "Órdago", "desc": "Roguelike de mus con santos, estampas y vinos.",
               "bg": "#0f2b3d", "theme": "#0f2b3d"},
    "tramite": {"src": "src/tramite.html", "name": "Último Trámite", "desc": "Papeleo de ultratumba: decide qué ánimas cruzan al Otro Lado.",
                "bg": "#1d1730", "theme": "#1d1730"},
}

SW = """const V='%(slug)s-%(ver)s';
const CORE=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png','./apple-touch-icon.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith('%(slug)s-')&&k!==V).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{
  const r=e.request;if(r.method!=='GET')return;
  if(r.mode==='navigate'){
    e.respondWith(fetch(r).then(res=>{const cp=res.clone();caches.open(V).then(c=>c.put('./index.html',cp));return res}).catch(()=>caches.match('./index.html')));
    return;
  }
  e.respondWith(caches.match(r).then(m=>m||fetch(r).then(res=>{if(res.ok||res.type==='opaque'){const cp=res.clone();caches.open(V).then(c=>c.put(r,cp))}return res})));
});
"""

WRAP_CSS = """<style>html{box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>"""


def sync_sources():
    # when the working copies next to this folder exist, they are the newest version
    import shutil
    for a, b in (("../farol/farol.html", "src/farol.html"), ("../ordago/ordago.html", "src/ordago.html"), ("../cripticos/cripticos.html", "src/cripticos.html"), ("../tramite/tramite.html", "src/tramite.html")):
        if os.path.exists(os.path.join(HERE, a)):
            shutil.copyfile(os.path.join(HERE, a), os.path.join(HERE, b))


def build(slug, g):
    out = os.path.join(HERE, slug)
    os.makedirs(out, exist_ok=True)
    src = open(os.path.join(HERE, g["src"]), encoding="utf-8").read()
    if not os.environ.get("KEEP_TEST_HOOK"):
        src = src.replace("if(location.protocol==='file:')window.__f=()=>S;\n", "").replace("if(location.protocol==='file:')window.__o=()=>S;\n", "")
        src = "\n".join(l for l in src.split("\n") if not l.startswith("if(location.protocol==='file:')window.__"))
    head, body = src.split("</style>", 1)
    extra = ('<link rel="manifest" href="manifest.webmanifest">\n<link rel="apple-touch-icon" href="apple-touch-icon.png">\n'
             '<link rel="icon" href="icon-192.png">\n<meta name="description" content="%s">\n' % g["desc"])
    html = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n' + extra + head + "</style>\n" + WRAP_CSS +
            "\n<!-- version " + VERSION + " -->\n</head>\n<body>\n" + body + "\n</body>\n</html>\n")
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(html)
    manifest = {"name": g["name"], "short_name": g["name"], "description": g["desc"], "lang": "es", "start_url": "./", "scope": "./",
                "display": "standalone", "orientation": "any", "background_color": g["bg"], "theme_color": g["theme"],
                "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
                          {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]}
    json.dump(manifest, open(os.path.join(out, "manifest.webmanifest"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(os.path.join(out, "sw.js"), "w").write(SW % {"slug": slug, "ver": VERSION})
    im = Image.open(os.path.join(HERE, slug + "-512.png")).convert("RGB")
    im.save(os.path.join(out, "icon-512.png"))
    im.resize((192, 192), Image.LANCZOS).save(os.path.join(out, "icon-192.png"))
    im.resize((180, 180), Image.LANCZOS).save(os.path.join(out, "apple-touch-icon.png"))
    print("built", slug, VERSION)


sync_sources()
for slug, g in GAMES.items():
    build(slug, g)
