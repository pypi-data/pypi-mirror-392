# Jugopy 1.0.9

Mini-framework WSGI en Python avec système de logs enrichi et design amélioré.

## 🆕 Nouveautés de la version 1.0.9

### ✨ Améliorations
- **Système de logs complet** : Logs détaillés dans toutes les fonctions
- **Design amélioré** : Pages d'erreur et d'accueil avec gradients et glassmorphism
- **Sécurité renforcée** : Messages d'erreur génériques pour la sécurité
- **Expérience développeur** : Flux d'exécution visible via les logs console

### 🔧 Fonctionnalités
- Configuration DB automatique via `conn_infos`
- Routing décorateur `@jugoRoute`
- Middlewares personnalisables
- Sessions et cookies
- Protection CSRF intégrée
- Validation email et slugification
- Templates Jinja2
- Gestion fichiers statiques avec cache

### 📦 Installation
```bash
pip install jugopy==1.0.9