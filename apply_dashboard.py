#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ajoute l'onglet Dashboard admin (KPIs, graphiques Chart.js, tableaux d'alertes).
Usage : python3 apply_dashboard.py
"""
import sys

PATH = "index.html"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

original_len = len(content)
patches_applied = 0

# ---------- PATCH 1 : boutons d'onglets + nouveau panneau Dashboard ----------
old1 = """        <div class="tab-buttons">
          <button class="active" data-tab="produits">Produits</button>
          <button data-tab="ajouter">Ajouter un produit</button>
        </div>
        <div class="tab-panel active" id="tab-produits">
"""

new1 = """        <div class="tab-buttons">
          <button class="active" data-tab="dashboard">Dashboard</button>
          <button data-tab="produits">Produits</button>
          <button data-tab="ajouter">Ajouter un produit</button>
        </div>
        <div class="tab-panel active" id="tab-dashboard">
          <div id="dashboard-loading" style="color:var(--gris-texte);padding:20px 0">Chargement des statistiques...</div>
          <div id="dashboard-content" style="display:none">
            <div id="kpi-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px;margin-bottom:32px"></div>
            <div style="display:grid;grid-template-columns:2fr 1fr;gap:20px;margin-bottom:32px" id="charts-row-1">
              <div class="glass" style="padding:20px;border-radius:var(--radius)">
                <h4 style="color:var(--or);font-weight:500;margin-bottom:14px;font-size:0.9rem">Commandes — 14 derniers jours</h4>
                <canvas id="chart-commandes" height="90"></canvas>
              </div>
              <div class="glass" style="padding:20px;border-radius:var(--radius)">
                <h4 style="color:var(--or);font-weight:500;margin-bottom:14px;font-size:0.9rem">Par catégorie</h4>
                <canvas id="chart-categories" height="90"></canvas>
              </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:32px" id="charts-row-2">
              <div class="glass" style="padding:20px;border-radius:var(--radius)">
                <h4 style="color:var(--or);font-weight:500;margin-bottom:14px;font-size:0.9rem">Produits les plus vus</h4>
                <canvas id="chart-vues" height="110"></canvas>
              </div>
              <div class="glass" style="padding:20px;border-radius:var(--radius)">
                <h4 style="color:var(--or);font-weight:500;margin-bottom:14px;font-size:0.9rem">Produits les plus commandés</h4>
                <canvas id="chart-commandes-produits" height="110"></canvas>
              </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px" id="dashboard-tables">
              <div class="glass" style="padding:18px;border-radius:var(--radius)">
                <h4 style="color:#e0554f;font-weight:500;margin-bottom:10px;font-size:0.85rem">⚠ Rupture de stock</h4>
                <div id="liste-rupture" style="font-size:0.82rem;color:var(--gris-texte)"></div>
              </div>
              <div class="glass" style="padding:18px;border-radius:var(--radius)">
                <h4 style="color:var(--or);font-weight:500;margin-bottom:10px;font-size:0.85rem">Messages récents</h4>
                <div id="liste-messages" style="font-size:0.82rem;color:var(--gris-texte)"></div>
              </div>
              <div class="glass" style="padding:18px;border-radius:var(--radius)">
                <h4 style="color:var(--or);font-weight:500;margin-bottom:10px;font-size:0.85rem">Dernières commandes</h4>
                <div id="liste-commandes" style="font-size:0.82rem;color:var(--gris-texte)"></div>
              </div>
            </div>
          </div>
        </div>
        <div class="tab-panel" id="tab-produits">
"""

if old1 in content:
    content = content.replace(old1, new1, 1)
    patches_applied += 1
    print("PATCH 1 (onglet Dashboard) : OK")
else:
    print("PATCH 1 (onglet Dashboard) : NON TROUVE")

# ---------- PATCH 2 : appel chargerDashboard() dans showAdmin ----------
old2 = """  function showAdmin() {
    document.getElementById('login-shell').style.display = 'none';
    document.getElementById('admin-shell').style.display = 'block';
    chargerProduitsAdmin();
  }
  if (adminToken) showAdmin();
"""

new2 = """  function showAdmin() {
    document.getElementById('login-shell').style.display = 'none';
    document.getElementById('admin-shell').style.display = 'block';
    chargerProduitsAdmin();
    chargerDashboard();
  }
  if (adminToken) showAdmin();
"""

if old2 in content:
    content = content.replace(old2, new2, 1)
    patches_applied += 1
    print("PATCH 2 (appel chargerDashboard) : OK")
else:
    print("PATCH 2 (appel chargerDashboard) : NON TROUVE")

# ---------- PATCH 3 : toutes les fonctions du dashboard ----------
old3 = """    tbody.querySelectorAll('[data-edit]').forEach(el => el.addEventListener('click', () => editerProduit(produits.find(p=>p.ID===el.dataset.edit))));
    tbody.querySelectorAll('[data-delete]').forEach(el => el.addEventListener('click', () => supprimerProduit(el.dataset.delete)));
  }

"""

new3 = """    tbody.querySelectorAll('[data-edit]').forEach(el => el.addEventListener('click', () => editerProduit(produits.find(p=>p.ID===el.dataset.edit))));
    tbody.querySelectorAll('[data-delete]').forEach(el => el.addEventListener('click', () => supprimerProduit(el.dataset.delete)));
  }

  let chartJsLoadPromise = null;
  function loadChartJs() {
    if (window.Chart) return Promise.resolve();
    if (chartJsLoadPromise) return chartJsLoadPromise;
    chartJsLoadPromise = new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.4/chart.umd.min.js';
      script.onload = resolve;
      script.onerror = () => reject(new Error('Impossible de charger Chart.js'));
      document.head.appendChild(script);
    });
    return chartJsLoadPromise;
  }

  let dashboardCharts = {};
  function detruireGraphique(id) {
    if (dashboardCharts[id]) { dashboardCharts[id].destroy(); delete dashboardCharts[id]; }
  }

  async function chargerDashboard() {
    const loadingEl = document.getElementById('dashboard-loading');
    const contentEl = document.getElementById('dashboard-content');
    loadingEl.style.display = 'block';
    loadingEl.textContent = 'Chargement des statistiques...';
    contentEl.style.display = 'none';
    try {
      await loadChartJs();
      const data = await API.get({ action: 'statistiques', token: adminToken });
      if (data.error) { loadingEl.textContent = data.error; return; }
      renderKpis(data.kpis);
      renderChartCommandes(data.commandesParJour);
      renderChartCategories(data.parCategorie);
      renderChartVues(data.plusConsultes);
      renderChartCommandesProduits(data.plusCommandes);
      renderListeRupture(data.produitsRuptureListe, data.produitsStockFaibleListe);
      renderListeMessages(data.messagesRecents);
      renderListeCommandes(data.dernieresCommandes);
      loadingEl.style.display = 'none';
      contentEl.style.display = 'block';
    } catch (err) {
      loadingEl.textContent = 'Erreur de chargement du dashboard : ' + err.message;
      console.error('[chargerDashboard]', err);
    }
  }

  function renderKpis(kpis) {
    const cartes = [
      { label: 'Produits', valeur: kpis.totalProduits },
      { label: 'Commandes', valeur: kpis.totalCommandes },
      { label: 'Chiffre d\\u2019affaires', valeur: formatPrice(kpis.chiffreAffaires) },
      { label: 'Vues totales', valeur: kpis.totalVues },
      { label: 'Clics WhatsApp', valeur: kpis.totalClicsWhatsapp },
      { label: 'Messages non lus', valeur: kpis.messagesNonLus, alerte: kpis.messagesNonLus > 0 },
      { label: 'Ruptures de stock', valeur: kpis.produitsRupture, alerte: kpis.produitsRupture > 0 }
    ];
    document.getElementById('kpi-grid').innerHTML = cartes.map(c => `
      <div class="glass" style="padding:18px;border-radius:var(--radius);text-align:center">
        <div style="font-size:1.6rem;font-weight:500;color:${c.alerte ? '#e0554f' : 'var(--or)'}">${c.valeur}</div>
        <div style="font-size:0.75rem;color:var(--gris-texte);margin-top:4px;text-transform:uppercase;letter-spacing:0.04em">${c.label}</div>
      </div>`).join('');
  }

  function chartDefaults() {
    return {
      plugins: { legend: { labels: { color: '#B8B2A4', font: { size: 11 } } } },
      scales: {
        x: { ticks: { color: '#B8B2A4', font: { size: 10 } }, grid: { color: 'rgba(212,175,55,0.08)' } },
        y: { ticks: { color: '#B8B2A4', font: { size: 10 } }, grid: { color: 'rgba(212,175,55,0.08)' }, beginAtZero: true }
      }
    };
  }

  function renderChartCommandes(commandesParJour) {
    detruireGraphique('commandes');
    const ctx = document.getElementById('chart-commandes');
    dashboardCharts.commandes = new Chart(ctx, {
      type: 'line',
      data: {
        labels: commandesParJour.map(j => j.date),
        datasets: [{
          label: 'Commandes',
          data: commandesParJour.map(j => j.commandes),
          borderColor: '#D4AF37', backgroundColor: 'rgba(212,175,55,0.15)',
          fill: true, tension: 0.35, pointRadius: 3, pointBackgroundColor: '#E8C766'
        }]
      },
      options: Object.assign({ responsive: true }, chartDefaults())
    });
  }

  function renderChartCategories(parCategorie) {
    detruireGraphique('categories');
    const ctx = document.getElementById('chart-categories');
    const palette = ['#D4AF37', '#E8C766', '#B8862F', '#8C6A24', '#F0DFA8', '#6B4F16'];
    dashboardCharts.categories = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: parCategorie.map(c => c.categorie),
        datasets: [{ data: parCategorie.map(c => c.count), backgroundColor: palette, borderColor: '#0B0B0B', borderWidth: 2 }]
      },
      options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { color: '#B8B2A4', font: { size: 10 }, boxWidth: 12 } } } }
    });
  }

  function renderChartVues(plusConsultes) {
    detruireGraphique('vues');
    const ctx = document.getElementById('chart-vues');
    dashboardCharts.vues = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: plusConsultes.map(p => p.nom),
        datasets: [{ label: 'Vues', data: plusConsultes.map(p => p.vues), backgroundColor: '#D4AF37', borderRadius: 4 }]
      },
      options: Object.assign({ responsive: true, indexAxis: 'y', plugins: { legend: { display: false } } }, chartDefaults())
    });
  }

  function renderChartCommandesProduits(plusCommandes) {
    detruireGraphique('commandesProduits');
    const ctx = document.getElementById('chart-commandes-produits');
    dashboardCharts.commandesProduits = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: plusCommandes.map(p => p.nom),
        datasets: [{ label: 'Quantité commandée', data: plusCommandes.map(p => p.quantite), backgroundColor: '#E8C766', borderRadius: 4 }]
      },
      options: Object.assign({ responsive: true, indexAxis: 'y', plugins: { legend: { display: false } } }, chartDefaults())
    });
  }

  function renderListeRupture(rupture, faible) {
    const el = document.getElementById('liste-rupture');
    if (!rupture.length && !faible.length) { el.innerHTML = '<p style="color:var(--gris-texte)">Tout est en stock.</p>'; return; }
    el.innerHTML = [
      ...rupture.map(p => `<div style="padding:6px 0;border-bottom:1px solid rgba(212,175,55,0.08)"><strong style="color:#e0554f">Épuisé</strong> — ${escapeHtml(p.nom)}</div>`),
      ...faible.map(p => `<div style="padding:6px 0;border-bottom:1px solid rgba(212,175,55,0.08)"><strong style="color:var(--or-clair)">Stock faible (${p.stock})</strong> — ${escapeHtml(p.nom)}</div>`)
    ].join('');
  }

  function renderListeMessages(messages) {
    const el = document.getElementById('liste-messages');
    if (!messages.length) { el.innerHTML = '<p style="color:var(--gris-texte)">Aucun message.</p>'; return; }
    el.innerHTML = messages.map(m => `
      <div style="padding:6px 0;border-bottom:1px solid rgba(212,175,55,0.08)">
        ${!m.lu ? '<strong style="color:var(--or-clair)">\\u25CF </strong>' : ''}${escapeHtml(m.nom || 'Anonyme')} — <span style="color:var(--gris-texte)">${escapeHtml(m.sujet || 'Sans sujet')}</span>
      </div>`).join('');
  }

  function renderListeCommandes(commandes) {
    const el = document.getElementById('liste-commandes');
    if (!commandes.length) { el.innerHTML = '<p style="color:var(--gris-texte)">Aucune commande.</p>'; return; }
    el.innerHTML = commandes.map(c => `
      <div style="padding:6px 0;border-bottom:1px solid rgba(212,175,55,0.08)">
        ${escapeHtml(c.nom || 'Client')} — ${escapeHtml(c.produit || '')} <span style="color:var(--or-clair)">${formatPrice(c.total)}</span>
      </div>`).join('');
  }

"""

if old3 in content:
    content = content.replace(old3, new3, 1)
    patches_applied += 1
    print("PATCH 3 (fonctions dashboard) : OK")
else:
    print("PATCH 3 (fonctions dashboard) : NON TROUVE")

if patches_applied == 0:
    print("\nAUCUN PATCH APPLIQUE. Verifie l'etat du fichier.")
    sys.exit(1)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n{patches_applied}/3 patch(es) applique(s). Fichier mis a jour : {PATH} ({original_len} -> {len(content)} caracteres).")
