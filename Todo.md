# 🚗 KOZ SERVICES - ERP & CRM Automobile

Plateforme complète de gestion pour concessionnaire automobile : demandes de financement, offres, ventes, maintenance, et e-commerce.

---

## 📦 Technologies utilisées

- **Backend** : Django 5.0, Django REST Framework
- **Frontend** : HTMX, TailwindCSS, DaisyUI, Chart.js
- **Base de données** : PostgreSQL (production), SQLite (dev)
- **Paiements** : Ligdicash (Mobile Money / Carte bancaire)
- **Conteneurisation** : Docker, Docker Compose

---

## 👥 Rôles & Fonctionnalités

### 👤 Client
- ✅ Inscription / Connexion sécurisée (JWT + sessions)
- ✅ Demande de financement de véhicule
- ✅ Upload de documents (CNI, quittance, relevé bancaire, etc.)
- ✅ Suivi du dossier (étapes : en attente, en cours, accordée, refusée)
- ✅ Consultation et acceptation/refus des offres
- ✅ Messagerie interne avec son commercial
- ✅ Gestion des maintenances (prochaines dates, historique)
- ✅ Simulation de crédit inversée (mensualité → prix accessible)
- ✅ Dashboard personnel avec indicateurs

### 💼 Commercial
- ✅ Dashboard avec liste des clients assignés
- ✅ Gestion des demandes de financement (changement d'étapes)
- ✅ Vérification et validation des documents clients
- ✅ Génération d’offres (liées à une demande ou simples)
- ✅ Gestion des ventes (statuts : conclue, perdue, en cours)
- ✅ Messagerie interne avec ses clients
- ✅ Planification des maintenances pour les clients
- ✅ Filtres avancés (HTMX) sur toutes les listes

### 👔 Directeur
- ✅ Dashboard KPI complet (cartes cliquables, graphiques)
- ✅ Graphique d’évolution du CA (Fidelis, Alios, KOZ, Cash)
- ✅ Création / gestion des utilisateurs (commerciaux, directeurs)
- ✅ Vue globale sur toutes les demandes, offres, ventes, maintenances
- ✅ Gestion du catalogue véhicules (CRUD)
- ✅ Gestion du catalogue produits (pièces détachées)
- ✅ Export des données (Excel - à venir)

---

## 🧩 Modules principaux

| Module | Description | Statut |
|--------|-------------|--------|
| **Authentification** | JWT + sessions, rôles client/commercial/directeur | ✅ 100% |
| **Demandes de financement** | Workflow complet (soumission, validation, étapes) | ✅ 100% |
| **Documents** | Upload, vérification, validation par le commercial | ✅ 100% |
| **Offres** | Génération, acceptation/refus, négociation, expiration auto | ✅ 100% |
| **Ventes** | Création auto (offres acceptées) + gestion manuelle | ✅ 100% |
| **Maintenances** | Suivi, rappels, priorité, origine véhicule (KOZ/externe) | ✅ 100% |
| **Messagerie** | Chat client ↔ commercial (HTMX) | ✅ 100% |
| **Dashboard DG** | KPI cliquables, graphique CA (4 courbes), filtres | ✅ 100% |
| **E-commerce** | Panier, commandes (APIs), Ligdicash en attente | 🔄 80% |
| **Produits / Véhicules** | CRUD complet côté ERP | ✅ 100% |
| **Notifications** | Email (SMTP) + WhatsApp Business | ⏳ 0% |

---

## 📊 Workflow métier principal
