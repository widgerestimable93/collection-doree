#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migre l'upload des photos de Google Drive vers Cloudinary.
Usage : python3 apply_cloudinary.py
"""
import sys

PATH = "index.html"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

original_len = len(content)
patches_applied = 0

# ---------- PATCH 1 : ajout config Cloudinary ----------
old1 = """const CONFIG = {
  API_URL: "https://script.google.com/macros/s/AKfycbyakOYRIl4OlsaAZ5pDLhSS0oTSgfuHwTqDfeh2YadiNJ9JOr0b7ydvckwrrpWSVJMAbQ/exec",
  WHATSAPP_NUMBER: "18297839254",
  CONTACT_EMAIL: "roseloreestimable86@gmail.com",
  SITE_NAME: "La Collection Dorée",
  CURRENCY: "USD" // à confirmer : HTG ou USD selon les prix réels
};"""

new1 = """const CONFIG = {
  API_URL: "https://script.google.com/macros/s/AKfycbyakOYRIl4OlsaAZ5pDLhSS0oTSgfuHwTqDfeh2YadiNJ9JOr0b7ydvckwrrpWSVJMAbQ/exec",
  WHATSAPP_NUMBER: "18297839254",
  CONTACT_EMAIL: "roseloreestimable86@gmail.com",
  SITE_NAME: "La Collection Dorée",
  CURRENCY: "USD", // à confirmer : HTG ou USD selon les prix réels
  CLOUDINARY_CLOUD_NAME: "brpyt6cw",
  CLOUDINARY_UPLOAD_PRESET: "collection_doree"
};"""

if old1 in content:
    content = content.replace(old1, new1, 1)
    patches_applied += 1
    print("PATCH 1 (config Cloudinary) : OK")
else:
    print("PATCH 1 (config Cloudinary) : NON TROUVE (peut-etre deja applique - verifie avec grep -c CLOUDINARY)")

# ---------- PATCH 2 : remplacement de la logique d'upload (Drive -> Cloudinary) ----------
old2 = """  async function traiterFichiers(files) {
    if (!files.length) return;
    uploadZone.style.borderColor = 'var(--or)';

    // 1) Aperçu local immédiat pour chaque fichier, AVANT tout upload
    const nouveaux = [];
    for (const file of Array.from(files)) {
      const dataUrl = await readAsDataURL(file);
      const item = { localSrc: dataUrl, status: 'uploading', url: null, error: null, name: file.name, file };
      items.push(item);
      nouveaux.push(item);
    }
    refreshPreview();

    // 2) Upload réel vers Drive, mise à jour de l'aperçu au fur et à mesure
    let ok = 0, erreurs = 0;
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

new2 = """  async function uploadVersCloudinary(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('upload_preset', CONFIG.CLOUDINARY_UPLOAD_PRESET);
    const url = `https://api.cloudinary.com/v1_1/${CONFIG.CLOUDINARY_CLOUD_NAME}/image/upload`;
    const res = await fetch(url, { method: 'POST', body: formData });
    const json = await res.json();
    if (!res.ok || json.error) {
      throw new Error((json.error && json.error.message) || `Erreur HTTP ${res.status}`);
    }
    return json.secure_url;
  }

  async function traiterFichiers(files) {
    if (!files.length) return;
    uploadZone.style.borderColor = 'var(--or)';

    // 1) Aperçu local immédiat pour chaque fichier, AVANT tout upload
    const nouveaux = [];
    for (const file of Array.from(files)) {
      const dataUrl = await readAsDataURL(file);
      const item = { localSrc: dataUrl, status: 'uploading', url: null, error: null, name: file.name, file };
      items.push(item);
      nouveaux.push(item);
    }
    refreshPreview();

    // 2) Upload réel vers Cloudinary, mise à jour de l'aperçu au fur et à mesure
    let ok = 0, erreurs = 0;
    progress.style.color = 'var(--or-clair)';
    for (const item of nouveaux) {
      console.log('[traiterFichiers] Upload de', item.name, 'vers Cloudinary, mimeType:', item.file.type);
      try {
        const secureUrl = await uploadVersCloudinary(item.file);
        item.status = 'done';
        item.url = secureUrl;
        ok++;
        console.log('[traiterFichiers] OK pour', item.name, '→', secureUrl);
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

if old2 in content:
    content = content.replace(old2, new2, 1)
    patches_applied += 1
    print("PATCH 2 (logique upload Cloudinary) : OK")
else:
    print("PATCH 2 (logique upload Cloudinary) : NON TROUVE (peut-etre deja applique - verifie avec grep -c uploadVersCloudinary)")

if patches_applied == 0:
    print("\nAUCUN PATCH APPLIQUE. Verifie l'etat du fichier avec :")
    print("  grep -c CLOUDINARY index.html")
    print("  grep -c uploadVersCloudinary index.html")
    sys.exit(1)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n{patches_applied}/2 patch(es) applique(s). Fichier mis a jour : {PATH} ({original_len} -> {len(content)} caracteres).")
