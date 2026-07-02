#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Applique le correctif "apercu instantane des photos uploadees" sur index.html.
Usage : python3 apply_fix.py
"""
import sys

PATH = "index.html"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

original_len = len(content)
patches_applied = 0

# ---------- PATCH 1 : bloc principal de logique upload ----------
old1 = """  // ---- Logique upload photos ----
  const photoInput  = document.getElementById('photo-input');
  const uploadZone  = document.getElementById('upload-zone');
  const preview     = document.getElementById('photos-preview');
  const progress    = document.getElementById('upload-progress');
  const photosHidden = document.getElementById('photos-hidden');

  let uploadedUrls = [];

  function updateHidden() {
    photosHidden.value = uploadedUrls.join(',');
  }

  function refreshPreview() {
    preview.innerHTML = uploadedUrls.map((url, i) => `
      <div style="position:relative;width:80px;height:80px">
        <img src="${url}" style="width:80px;height:80px;object-fit:cover;border-radius:var(--radius);border:1px solid rgba(212,175,55,0.3)">
        <button type="button" onclick="removePhoto(${i})" style="position:absolute;top:-6px;right:-6px;width:20px;height:20px;border-radius:50%;background:#e0554f;color:#fff;font-size:0.7rem;display:flex;align-items:center;justify-content:center">✕</button>
      </div>`).join('');
  }

  window.removePhoto = function(index) {
    uploadedUrls.splice(index, 1);
    updateHidden();
    refreshPreview();
  };

  async function uploadFichier(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const base64 = e.target.result.split(',')[1];
        const res = await API.post('uploadImage', {
          base64, mimeType: file.type, nom: file.name
        }, adminToken);
        if (res.success) resolve(res.url);
        else reject(new Error(res.error || 'Erreur upload'));
      };
      reader.readAsDataURL(file);
    });
  }

  async function traiterFichiers(files) {
    if (!files.length) return;
    progress.textContent = 'Upload en cours...';
    uploadZone.style.borderColor = 'var(--or)';
    let ok = 0;
    for (const file of Array.from(files)) {
      try {
        const url = await uploadFichier(file);
        uploadedUrls.push(url);
        ok++;
        progress.textContent = `${ok}/${files.length} photo(s) uploadée(s)...`;
        refreshPreview();
        updateHidden();
      } catch (err) {
        progress.style.color = '#e0554f';
        progress.textContent = 'Erreur : ' + err.message;
      }
    }
    progress.style.color = 'var(--or-clair)';
    progress.textContent = ok + ' photo(s) prête(s).';
    uploadZone.style.borderColor = 'rgba(212,175,55,0.3)';
  }

  photoInput.addEventListener('change', (e) => traiterFichiers(e.target.files));"""

new1 = """  // ---- Logique upload photos ----
  const photoInput  = document.getElementById('photo-input');
  const uploadZone  = document.getElementById('upload-zone');
  const preview     = document.getElementById('photos-preview');
  const progress    = document.getElementById('upload-progress');
  const photosHidden = document.getElementById('photos-hidden');

  let uploadedUrls = [];   // URLs Drive confirmées (envoyées au serveur)
  let items = [];          // { localSrc, status:'uploading'|'done'|'error', url, error, name, file }

  function updateHidden() {
    photosHidden.value = uploadedUrls.join(',');
  }

  function refreshPreview() {
    preview.innerHTML = items.map((item, i) => {
      const src = item.status === 'done' ? item.url : item.localSrc;
      const overlay = item.status === 'uploading'
        ? `<div style="position:absolute;inset:0;background:rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;border-radius:var(--radius);color:#fff;font-size:0.65rem">...</div>`
        : item.status === 'error'
        ? `<div style="position:absolute;inset:0;background:rgba(224,85,79,0.55);display:flex;align-items:center;justify-content:center;border-radius:var(--radius);color:#fff;font-size:1rem" title="${(item.error||'').replace(/"/g,'')}">⚠</div>`
        : '';
      const borderColor = item.status === 'error' ? '#e0554f' : 'rgba(212,175,55,0.3)';
      return `
      <div style="position:relative;width:80px;height:80px">
        <img src="${src}" style="width:80px;height:80px;object-fit:cover;border-radius:var(--radius);border:1px solid ${borderColor}">
        ${overlay}
        <button type="button" onclick="removePhoto(${i})" style="position:absolute;top:-6px;right:-6px;width:20px;height:20px;border-radius:50%;background:#e0554f;color:#fff;font-size:0.7rem;display:flex;align-items:center;justify-content:center;border:none;cursor:pointer">✕</button>
      </div>`;
    }).join('');
  }

  window.removePhoto = function(index) {
    items.splice(index, 1);
    uploadedUrls = items.filter(it => it.status === 'done').map(it => it.url);
    updateHidden();
    refreshPreview();
  };

  function readAsDataURL(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = () => reject(new Error('Lecture du fichier impossible'));
      reader.readAsDataURL(file);
    });
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

    // 2) Upload réel vers Drive, mise à jour de l'aperçu au fur et à mesure
    let ok = 0, erreurs = 0;
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
    }

    uploadZone.style.borderColor = erreurs ? '#e0554f' : 'rgba(212,175,55,0.3)';
    if (erreurs) {
      progress.style.color = '#e0554f';
      progress.textContent = `${ok} photo(s) prête(s), ${erreurs} échec(s). Survole ⚠ sur la vignette pour voir l'erreur.`;
    } else {
      progress.style.color = 'var(--or-clair)';
      progress.textContent = ok + ' photo(s) prête(s).';
    }
  }

  photoInput.addEventListener('change', (e) => { traiterFichiers(e.target.files); photoInput.value = ''; });"""

if old1 in content:
    content = content.replace(old1, new1, 1)
    patches_applied += 1
    print("PATCH 1 (logique upload) : OK")
else:
    print("PATCH 1 (logique upload) : NON TROUVE - le fichier a peut-etre deja ete modifie ou differe legerement.")

# ---------- PATCH 2 : editerProduit (chargement des photos existantes en edition) ----------
old2 = """    form.photos.value = (p.Photos || []).join(', '); form.disponible.checked = !!p.Disponible; form.vedette.checked = !!p.Vedette;
    uploadedUrls = p.Photos || [];
    updateHidden(); refreshPreview();"""

new2 = """    form.photos.value = (p.Photos || []).join(', '); form.disponible.checked = !!p.Disponible; form.vedette.checked = !!p.Vedette;
    items = (p.Photos || []).map(url => ({ localSrc: url, status: 'done', url, error: null, name: '', file: null }));
    uploadedUrls = items.map(it => it.url);
    updateHidden(); refreshPreview();"""

if old2 in content:
    content = content.replace(old2, new2, 1)
    patches_applied += 1
    print("PATCH 2 (edition produit) : OK")
else:
    print("PATCH 2 (edition produit) : NON TROUVE - le fichier a peut-etre deja ete modifie ou differe legerement.")

# ---------- PATCH 3 : reinitialisation lors de l'annulation ----------
old3 = """  document.getElementById('cancel-edit').addEventListener('click', () => {
    uploadedUrls = []; updateHidden(); refreshPreview(); progress.textContent = '';
  });"""

new3 = """  document.getElementById('cancel-edit').addEventListener('click', () => {
    items = []; uploadedUrls = []; updateHidden(); refreshPreview(); progress.textContent = '';
  });"""

if old3 in content:
    content = content.replace(old3, new3, 1)
    patches_applied += 1
    print("PATCH 3 (annulation) : OK")
else:
    print("PATCH 3 (annulation) : NON TROUVE - le fichier a peut-etre deja ete modifie ou differe legerement.")

if patches_applied == 0:
    print("\nAUCUN PATCH APPLIQUE. Le fichier index.html ne correspond pas a la version attendue.")
    print("Aucune modification n'a ete faite (par securite).")
    sys.exit(1)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n{patches_applied}/3 patch(es) applique(s). Fichier mis a jour : {PATH} ({original_len} -> {len(content)} caracteres).")
