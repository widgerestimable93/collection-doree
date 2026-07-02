#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ajoute des console.log detailles dans API.post et traiterFichiers.
A lancer APRES avoir deja applique apply_fix.py (le premier correctif).
Usage : python3 apply_logs.py
"""
import sys

PATH = "index.html"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

original_len = len(content)
patches_applied = 0

# ---------- PATCH A : API.post avec logs ----------
oldA = """const API = {
  async get(params) {
    const url = new URL(CONFIG.API_URL);
    Object.keys(params).forEach(k => url.searchParams.set(k, params[k]));
    const res = await fetch(url.toString());
    return res.json();
  },
  async post(action, data, token) {
    const res = await fetch(CONFIG.API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify({ action, data, token })
    });
    return res.json();
  }
};"""

newA = """const API = {
  async get(params) {
    const url = new URL(CONFIG.API_URL);
    Object.keys(params).forEach(k => url.searchParams.set(k, params[k]));
    const res = await fetch(url.toString());
    return res.json();
  },
  async post(action, data, token) {
    console.log('[API.post] →', action, { data: (data && data.base64) ? { ...data, base64: `(${data.base64.length} caractères, tronqué)` } : data, tokenPresent: !!token });
    let res;
    try {
      res = await fetch(CONFIG.API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: JSON.stringify({ action, data, token })
      });
    } catch (networkErr) {
      console.error('[API.post] Erreur réseau (fetch a échoué) pour', action, networkErr);
      throw networkErr;
    }
    console.log('[API.post] ←', action, 'HTTP', res.status, res.statusText);
    const rawText = await res.text();
    console.log('[API.post] ← corps brut (', rawText.length, 'caractères ) :', rawText.slice(0, 2000));
    let json;
    try {
      json = JSON.parse(rawText);
    } catch (parseErr) {
      console.error('[API.post] Réponse non-JSON reçue pour', action, '— probablement une page HTML (redirection de connexion Google, erreur de déploiement GAS, etc.)', parseErr);
      throw new Error('Réponse serveur invalide (non-JSON). Voir console pour le détail.');
    }
    console.log('[API.post] JSON parsé pour', action, ':', json);
    return json;
  }
};"""

if oldA in content:
    content = content.replace(oldA, newA, 1)
    patches_applied += 1
    print("PATCH A (API.post logs) : OK")
else:
    print("PATCH A (API.post logs) : NON TROUVE")

# ---------- PATCH B : logs dans la boucle d'upload ----------
oldB = """    let ok = 0, erreurs = 0;
    progress.style.color = 'var(--or-clair)';
    for (const item of nouveaux) {
      try {
        const base64 = item.localSrc.split(',')[1];
        const res = await API.post('uploadImage', {
          base64, mimeType: item.file.type, nom: item.file.name
        }, adminToken);
        if (res && res.success) {
          item.status = 'done';
          item.url = res.url;
          ok++;
        } else {
          item.status = 'error';
          item.error = (res && res.error) || 'Erreur upload';
          erreurs++;
        }
      } catch (err) {
        item.status = 'error';
        item.error = err.message || 'Erreur réseau';
        erreurs++;
      }
      uploadedUrls = items.filter(it => it.status === 'done').map(it => it.url);
      updateHidden();
      refreshPreview();
      progress.textContent = `${ok}/${nouveaux.length} photo(s) uploadée(s)` + (erreurs ? `, ${erreurs} erreur(s)` : '') + '...';
    }"""

newB = """    let ok = 0, erreurs = 0;
    progress.style.color = 'var(--or-clair)';
    for (const item of nouveaux) {
      console.log('[traiterFichiers] Upload de', item.name, '— taille base64:', item.localSrc.length, 'mimeType:', item.file.type);
      try {
        const base64 = item.localSrc.split(',')[1];
        const res = await API.post('uploadImage', {
          base64, mimeType: item.file.type, nom: item.file.name
        }, adminToken);
        if (res && res.success) {
          item.status = 'done';
          item.url = res.url;
          ok++;
          console.log('[traiterFichiers] OK pour', item.name, '→', res.url);
        } else {
          item.status = 'error';
          item.error = (res && res.error) || 'Erreur upload';
          erreurs++;
          console.error('[traiterFichiers] ECHEC pour', item.name, '— réponse serveur:', res);
        }
      } catch (err) {
        item.status = 'error';
        item.error = err.message || 'Erreur réseau';
        erreurs++;
        console.error('[traiterFichiers] EXCEPTION pour', item.name, ':', err);
      }
      uploadedUrls = items.filter(it => it.status === 'done').map(it => it.url);
      updateHidden();
      refreshPreview();
      progress.textContent = `${ok}/${nouveaux.length} photo(s) uploadée(s)` + (erreurs ? `, ${erreurs} erreur(s)` : '') + '...';
    }"""

if oldB in content:
    content = content.replace(oldB, newB, 1)
    patches_applied += 1
    print("PATCH B (logs boucle upload) : OK")
else:
    print("PATCH B (logs boucle upload) : NON TROUVE")

if patches_applied == 0:
    print("\nAUCUN PATCH APPLIQUE. Le fichier index.html ne correspond pas a la version attendue (le premier correctif apply_fix.py a-t-il bien ete applique ?).")
    sys.exit(1)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n{patches_applied}/2 patch(es) applique(s). Fichier mis a jour : {PATH} ({original_len} -> {len(content)} caracteres).")
