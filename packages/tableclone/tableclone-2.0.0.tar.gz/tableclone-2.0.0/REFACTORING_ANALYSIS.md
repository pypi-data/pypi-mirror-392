# TableClone : Analyse et Plan de Refactoring

**Date de l'analyse** : Octobre 2025  
**Version actuelle** : ~5600 lignes Python, 9 plateformes supportées  
**Objectif** : Simplifier l'architecture tout en préservant les connaissances métier

---

## 📊 Vue d'ensemble du projet

TableClone est un outil de synchronisation de données entre plateformes hétérogènes (Airtable, Bubble, PostgreSQL, SQLite, Google Drive, Excel, etc.). Il utilise Pandas comme couche d'abstraction pour normaliser et comparer les données.

### Statistiques du code
- **~5600 lignes** de code Python
- **9 plateformes** supportées
- **2 types de tâches** : sync (table-to-table) et backup (container-to-container)
- **Volumes traités** : 1k à 100k lignes par table

---

## ✅ Ce qui est BIEN conçu (à préserver)

### 1. Système d'options (`utils.py`)
Le système `Option` / `OptionSet` / `OptionValues` est **excellent** :
- ✅ Validation des types
- ✅ Valeurs par défaut
- ✅ Gestion des options incompatibles
- ✅ Énumérations
- ✅ Auto-documentation

**→ À GARDER et potentiellement extraire en bibliothèque séparée**

### 2. Architecture d'abstraction (concept)
- **Pattern Factory** bien implémenté (`factory.py`)
- **Hiérarchie de classes** logique (Platform → Table → Container)
- **Mixins** élégants (`PaginatedTable`, `InsertUpdateUpsertTable`)
- **Séparation des responsabilités** claire

**→ Concept solide, mais implémentation à simplifier**

### 3. Field Mapping
```python
FIELD_MAPPING = FieldMapper(to_generic, from_generic)
```
- ✅ Bonne approche pour gérer l'hétérogénéité des types
- ✅ Permet l'interopérabilité entre plateformes

**→ À conserver tel quel**

### 4. Gestion des cas réels
Le code montre une vraie expérience terrain :
- Normalisation des dates avec patterns regex
- Gestion des colonnes manquantes/vides
- Truncation des textes longs (Airtable 100k chars)
- Préprocessing des URLs (Bubble `//` → `https://`)

**→ Connaissance métier précieuse à préserver**

---

## ⚠️ Problèmes identifiés

### 1. Complexité excessive de la hiérarchie

**Problème** : 6 niveaux de classes abstraites imbriquées
```
Platform
  └─ RestAPIPlatform
PlatformObject
  └─ Table
      └─ PaginatedTable
          └─ InsertUpdateUpsertTable
```

**Conséquences** :
- Difficile de comprendre quel niveau implémente quelle méthode
- `NotImplementedError` éparpillés (~30-40% du code jamais exécuté)
- `@abstractmethod` sans vraiment être abstrait
- Violation du principe YAGNI

**Solution** : Réduire à 3 niveaux maximum

### 2. Pandas comme couche d'abstraction : mauvais choix

**Problèmes** :
- Perte d'information (`np.nan` vs `None` vs chaîne vide vs colonne absente)
- Types chaotiques (`object` pour tout)
- Index obligatoire → jonglage constant avec `reset_index()`, `set_index()`
- Mémoire importante pour des opérations simples
- Contorsions partout : `df.replace({np.nan: None})`

**Solution** : Format intermédiaire léger (dict/dataclass) + moteur de calcul optionnel (Polars/DuckDB si besoin de perf)

### 3. Gestion du "unique ID" : cauchemar

**4 façons différentes de gérer les IDs** :
1. `NATIVE_ID_NAME` (ex: `record_id` pour Airtable)
2. `OPT_UNIQUE_ID_COLUMN` (PostgreSQL/SQLite)
3. `OPT_OVERRIDE_NATIVE_ID_NAME`
4. `table_index_name()` qui préfixe avec `tc_`

**Conséquence** : Logique métier polluée par détails d'implémentation

**Solution** : Unifier en un seul concept d'ID universel

### 4. Comparaison des DataFrames : inefficace

```python
updated_values_ids = dst_df_filtered.compare(src_df_filtered).index
```

**Problèmes** :
- `DataFrame.compare()` coûteux en mémoire
- Normalisation des dates non déterministe (échantillonnage aléatoire)
- Pas de cache
- Export CSV pour debug = signe d'opacité

**Solution** : Module dédié `TableComparator` avec algorithme clair

### 5. Gestion des credentials : dangereuse

```python
def __init__(self, platform_root_path="", secret_string=None, options={})
```

**Problèmes** :
- `secret_string` en paramètre → risque de logging
- Pas de keyring/vault
- Substitution env vars dans CLI mais parsing dans Platform

**Solution** : Module `tableclone.auth` avec keyring

### 6. Incohérences et code mort

**Exemples** :
- Bubble : `dump_df`, `get_table_schema` → `NotImplementedError`
- SQLite : `get_bulk_raw_data` → `NotImplementedError` mais jamais appelé
- Pattern `make_record_X_from_df_row` avec types de retour variables (dict/tuple/str)

**Solution** : Supprimer le code mort, unifier les contrats

---

## 🎯 Plan de Refactoring Incrémental (6 mois)

### Phase 1 : Stabilisation (2 mois)

**Objectif** : Sécuriser l'existant avant de modifier

#### Semaine 1-2 : Tests d'intégration
```python
# tests/integration/test_platforms.py
def test_airtable_sync():
    """Test sync Airtable → SQLite avec données réelles"""
    config = load_test_config("airtable_sqlite.json")
    task = TableSyncTask(config)
    result = task.process()
    assert result["inserted_row_count"] > 0

def test_bubble_backup():
    """Test backup Bubble → Excel"""
    # ...
```

**Tâches** :
- [ ] Créer tests pour chaque plateforme supportée
- [ ] Utiliser pytest avec fixtures
- [ ] Viser 60%+ de couverture sur les chemins fonctionnels

#### Semaine 3-4 : Documentation
- [ ] Documenter quels endpoints/méthodes fonctionnent
- [ ] Identifier les fonctionnalités cassées/incomplètes
- [ ] Créer matrice de compatibilité (plateforme × opération)

#### Semaine 5-8 : Nettoyage
- [ ] Supprimer tous les `NotImplementedError` non utilisés
- [ ] Identifier et marquer le code deprecated
- [ ] Créer CHANGELOG.md avec historique

### Phase 2 : Simplification (3 mois)

**Objectif** : Simplifier l'architecture sans casser l'existant

#### Mois 1 : Remplacer Pandas par modèle simple

**Architecture cible** :
```python
from dataclasses import dataclass
from typing import Iterator

@dataclass
class TableData:
    """Format intermédiaire léger - pas de dépendance Pandas"""
    schema: dict[str, FieldType]
    rows: list[dict] | Iterator[dict]  # Lazy si gros volumes
    unique_id_field: str
    
    @classmethod
    def from_platform(cls, table: Table):
        """Factory depuis vos Tables existantes"""
        rows = table.get_all()  # Déjà une liste de dicts !
        schema = {f.name: f.generic_type for f in table.get_table_schema()}
        return cls(
            schema=schema,
            rows=rows,
            unique_id_field=table.unique_id_column or table.NATIVE_ID_NAME
        )
    
    # Conversion optionnelle si besoin de perf
    def to_polars(self):
        """Uniquement si opérations lourdes nécessaires"""
        import polars as pl
        return pl.DataFrame(self.rows)
```

**Migration progressive** :
```python
# Étape 1 : Ajouter sans casser
class Table:
    def get_all_as_df(self):  # GARDER (legacy)
        return pd.DataFrame(self.get_all())
    
    def get_all_as_tabledata(self):  # NOUVEAU
        return TableData.from_platform(self)

# Étape 2 : Migrer les tâches une par une
class TableSyncTask:
    def _process_impl_v2(self):  # Nouvelle version
        src = self.source.get_all_as_tabledata()
        dst = self.destination.get_all_as_tabledata()
        # ...

# Étape 3 : Supprimer les anciennes méthodes
```

#### Mois 2 : Unifier la gestion des IDs

**Concept unique** :
```python
@dataclass
class UniqueIdentifier:
    """Représentation universelle d'un identifiant unique"""
    field_name: str  # Nom du champ (peut être "id", "record_id", "uuid", etc.)
    is_native: bool  # True si ID natif de la plateforme
    value_type: type  # str, int, UUID...
    
    def extract_from(self, record: dict):
        """Extrait la valeur de l'ID depuis un record"""
        return record.get(self.field_name)

class Table:
    @property
    def unique_identifier(self) -> UniqueIdentifier:
        """Chaque table expose son système d'ID de manière uniforme"""
        if hasattr(self, 'NATIVE_ID_NAME'):
            return UniqueIdentifier(
                field_name=self.NATIVE_ID_NAME,
                is_native=True,
                value_type=str
            )
        elif self.option_values.get(self.OPT_UNIQUE_ID_COLUMN):
            col = self.option_values.get(self.OPT_UNIQUE_ID_COLUMN)
            return UniqueIdentifier(
                field_name=col,
                is_native=False,
                value_type=str  # Détecter automatiquement ?
            )
        else:
            raise ValueError("No unique identifier configured")
```

**Avantages** :
- Plus de `table_index_name()`, `tc_` prefix, etc.
- Logique métier propre : "compare by unique_identifier"
- Facile à tester et raisonner

#### Mois 3 : Extraire la comparaison

**Module dédié** :
```python
# tableclone/processing/comparator.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class DiffResult:
    to_insert: list[dict]  # Records à insérer
    to_update: list[dict]  # Records à mettre à jour
    to_delete: list[dict]  # Records à supprimer (si mode delete activé)
    unchanged: int  # Nombre de records identiques

class TableComparator:
    """Extrait la logique de comparaison de TableSyncTask"""
    
    @staticmethod
    def diff(
        src: TableData, 
        dst: TableData, 
        mapping: dict[str, str],
        options: dict = {}
    ) -> DiffResult:
        """
        Compare deux tables et retourne les différences.
        
        Implémentation simple (dict pur) :
        - Rapide jusqu'à ~50k lignes
        - Pas de dépendance
        
        Si besoin de perf sur >100k lignes, utiliser Polars/DuckDB
        """
        src_by_id = {
            src.unique_id_field: record 
            for record in src.rows
        }
        dst_by_id = {
            dst.unique_id_field: record 
            for record in dst.rows
        }
        
        to_insert = []
        to_update = []
        unchanged = 0
        
        for src_id, src_record in src_by_id.items():
            if src_id not in dst_by_id:
                to_insert.append(src_record)
            else:
                dst_record = dst_by_id[src_id]
                if TableComparator._records_differ(src_record, dst_record, mapping):
                    to_update.append(src_record)
                else:
                    unchanged += 1
        
        # Calcul des suppressions si nécessaire
        to_delete = []
        if options.get("delete_mode"):
            to_delete = [
                record for dst_id, record in dst_by_id.items()
                if dst_id not in src_by_id
            ]
        
        return DiffResult(
            to_insert=to_insert,
            to_update=to_update,
            to_delete=to_delete,
            unchanged=unchanged
        )
    
    @staticmethod
    def _records_differ(src: dict, dst: dict, mapping: dict) -> bool:
        """Compare deux records selon le mapping"""
        for src_col, dst_col in mapping.items():
            src_val = src.get(src_col)
            dst_val = dst.get(dst_col)
            
            # Normalisation basique
            if src_val != dst_val:
                # Ignorer None vs "" vs [] ?
                if src_val in (None, "", []) and dst_val in (None, "", []):
                    continue
                return True
        
        return False
```

**Note performance** : Si besoin d'optimisation sur >100k lignes :
```python
def diff_optimized(src: TableData, dst: TableData, mapping: dict):
    """Version optimisée avec Polars (optionnel)"""
    import polars as pl
    
    src_pl = pl.DataFrame(src.rows)
    dst_pl = pl.DataFrame(dst.rows)
    
    # Anti-join pour nouveaux records
    to_insert = src_pl.join(
        dst_pl, 
        on=src.unique_id_field, 
        how="anti"
    ).to_dicts()
    
    # Join + filter pour updates
    # ...
```

### Phase 3 : Découplage (2 mois)

#### Mois 1 : Credentials et configuration

**Module auth** :
```python
# tableclone/auth/__init__.py

from abc import ABC, abstractmethod
import keyring
import os

class CredentialProvider(ABC):
    @abstractmethod
    def get_secret(self, platform: str, key: str) -> str:
        pass

class KeyringProvider(CredentialProvider):
    """Stockage sécurisé via keyring système"""
    def get_secret(self, platform: str, key: str) -> str:
        return keyring.get_password(f"tableclone_{platform}", key)

class EnvVarProvider(CredentialProvider):
    """Variables d'environnement (CI/CD)"""
    def get_secret(self, platform: str, key: str) -> str:
        var_name = f"TABLECLONE_{platform.upper()}_{key.upper()}"
        return os.environ[var_name]

class Platform:
    def __init__(self, credential_provider: CredentialProvider = None):
        self.cred_provider = credential_provider or EnvVarProvider()
        self.parse_auth_information()
```

**Configuration avec Pydantic** :
```python
# tableclone/config.py

from pydantic import BaseModel, Field, validator
from typing import Optional

class PlatformConfig(BaseModel):
    platform: str
    platform_root_path: Optional[str]
    options: dict = {}
    
    @validator('platform')
    def platform_must_be_supported(cls, v):
        if v not in PLATFORMS:
            raise ValueError(f"Unsupported platform: {v}")
        return v

class TableConfig(BaseModel):
    alias: str
    api_identifier: str
    platform: PlatformConfig
    options: dict = {}

class SyncTaskConfig(BaseModel):
    source: TableConfig
    destination: TableConfig
    options: dict = {}
    
    # Validation automatique des types, valeurs par défaut, etc.
```

#### Mois 2 : Système d'événements

**Remplacer webhooks hardcodés** :
```python
# tableclone/events.py

from dataclasses import dataclass
from typing import Callable, Any
from enum import Enum

class TaskEvent(Enum):
    STARTED = "started"
    PROGRESS = "progress"
    SUCCESS = "success"
    ERROR = "error"

@dataclass
class Event:
    type: TaskEvent
    data: dict[str, Any]
    task_id: str

class EventBus:
    def __init__(self):
        self._handlers: dict[TaskEvent, list[Callable]] = {}
    
    def subscribe(self, event_type: TaskEvent, handler: Callable):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def publish(self, event: Event):
        for handler in self._handlers.get(event.type, []):
            handler(event)

# Usage
class TableSyncTask:
    def __init__(self, config: dict, event_bus: EventBus = None):
        self.event_bus = event_bus or EventBus()
    
    def _process_impl(self):
        self.event_bus.publish(Event(
            type=TaskEvent.STARTED,
            data={"source": str(self.source)},
            task_id=self.config.get("task_id")
        ))
        
        # ... traitement ...
        
        self.event_bus.publish(Event(
            type=TaskEvent.SUCCESS,
            data={"inserted": 10, "updated": 5},
            task_id=self.config.get("task_id")
        ))

# Webhook devient un handler parmi d'autres
def webhook_handler(event: Event):
    if event.type == TaskEvent.SUCCESS:
        requests.post(webhook_url, json=event.data)

event_bus.subscribe(TaskEvent.SUCCESS, webhook_handler)
```

### Phase 4 : Observabilité (1 mois)

#### Structured logging
```python
# tableclone/logging.py

import structlog

def setup_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    )

logger = structlog.get_logger()

# Usage
logger.info(
    "table_sync_completed",
    task_id="sync_123",
    source="airtable:base1/table1",
    destination="sqlite:db.sqlite:table1",
    inserted=10,
    updated=5,
    duration_ms=1250
)
```

#### Métriques
```python
# tableclone/metrics.py

from dataclasses import dataclass
from datetime import datetime

@dataclass
class SyncMetrics:
    task_id: str
    start_time: datetime
    end_time: datetime
    rows_compared: int
    rows_inserted: int
    rows_updated: int
    rows_deleted: int
    errors: list[str]
    
    @property
    def duration_seconds(self) -> float:
        return (self.end_time - self.start_time).total_seconds()
    
    def to_dict(self):
        return {
            "task_id": self.task_id,
            "duration_seconds": self.duration_seconds,
            "rows_compared": self.rows_compared,
            "rows_modified": self.rows_inserted + self.rows_updated + self.rows_deleted,
            "success": len(self.errors) == 0
        }
```

#### Dry-run mode
```python
class TableSyncTask:
    def _process_impl(self, dry_run: bool = False):
        diff = TableComparator.diff(src, dst, mapping)
        
        if dry_run:
            # Prévisualisation sans exécution
            return {
                "preview": True,
                "to_insert": len(diff.to_insert),
                "to_update": len(diff.to_update),
                "sample_insert": diff.to_insert[:5],
                "sample_update": diff.to_update[:5]
            }
        
        # Exécution réelle
        if diff.to_insert:
            self.destination.insert(diff.to_insert)
        # ...
```

---

## 🏗️ Architecture cible

### Hiérarchie simplifiée (3 niveaux max)

```
Platform (auth, list, create)
  ├─ RestAPIPlatform (si API REST)
  └─ ... (autres types si nécessaire)

Table (get, insert, update, schema)
  └─ (pas de sous-classes sauf si vraiment nécessaire)

Container (multi-tables)
  └─ (pas de sous-classes)

Task (orchestration)
  ├─ TableSyncTask
  └─ ContainerBackupTask
```

**Principe** : Composition > Héritage

### Format de données universel

```python
TableData (simple dataclass)
  ↓
Operations légères (dict manipulation)
  ↓
Si besoin perf: Polars/DuckDB (optionnel)
  ↓
Retour à TableData
```

### Flux de données

```
Platform.get_all() → list[dict]
  ↓
TableData (format léger)
  ↓
TableComparator.diff() → DiffResult
  ↓
Platform.insert/update() → list[dict]
```

---

## 🛠️ Technologies recommandées

### Obligatoires
- ✅ **Pydantic v2** : Validation de configuration
- ✅ **Pytest** : Tests (coverage >70%)
- ✅ **Mypy** : Type hints stricts
- ✅ **Structlog** : Logging structuré
- ✅ **Keyring** : Credentials sécurisés

### Optionnelles (si besoin de performance)
- 🔧 **Polars** : Remplacement Pandas (3-10x plus rapide)
- 🔧 **DuckDB** : SQL sur DataFrames (5-15x plus rapide)
- 🔧 **FireDucks** : Drop-in Pandas replacement (mais licence propriétaire)

**Règle** : Implémenter d'abord en dict pur Python. Optimiser avec Polars/DuckDB seulement si mesure démontre un besoin.

---

## 📋 Actions prioritaires

### Court terme (Semaines 1-4)

#### Semaine 1
- [ ] Créer `tests/integration/` avec 1 test par plateforme
- [ ] Installer pytest, configurer coverage
- [ ] Créer matrice de compatibilité (plateformes × opérations)

#### Semaine 2
- [ ] Documenter toutes les méthodes publiques (docstrings)
- [ ] Créer CHANGELOG.md
- [ ] Identifier et lister le code mort (`NotImplementedError`)

#### Semaine 3
- [ ] Supprimer code mort (branch séparée)
- [ ] Merger classes redondantes (ex: certains niveaux hiérarchie)
- [ ] Créer `tableclone/core/models.py` avec `TableData`

#### Semaine 4
- [ ] Implémenter `TableData.from_platform()` pour 1 plateforme (Airtable)
- [ ] Tester les 2 approches en parallèle (Pandas vs TableData)
- [ ] Mesurer performances et mémoire

### Moyen terme (Mois 2-4)

#### Mois 2
- [ ] Migrer toutes les plateformes vers `TableData`
- [ ] Créer `TableComparator` avec implémentation dict pur
- [ ] Garder méthodes Pandas en fallback (deprecated)

#### Mois 3
- [ ] Implémenter `UniqueIdentifier` universel
- [ ] Refactorer `TableSyncTask` avec nouvelle architecture
- [ ] Migrer tests sur nouvelle architecture

#### Mois 4
- [ ] Créer module `tableclone.auth`
- [ ] Remplacer `secret_string` par `CredentialProvider`
- [ ] Intégrer Pydantic pour config

### Long terme (Mois 5-6)

#### Mois 5
- [ ] Système d'événements (`EventBus`)
- [ ] Structured logging (structlog)
- [ ] Métriques et dry-run mode

#### Mois 6
- [ ] Supprimer dépendance Pandas (si plus nécessaire)
- [ ] Ajouter Polars/DuckDB **si** benchmarks montrent besoin
- [ ] Documentation complète (Sphinx)
- [ ] CI/CD (GitHub Actions)

---

## 🎯 Critères de succès

### Métriques quantitatives
- **Tests** : Coverage >70% sur code fonctionnel
- **Performance** : Pas de régression sur sync 10-100k lignes
- **Mémoire** : Réduction 30-50% (sans Pandas)
- **Code** : Réduction ~20% lignes (suppression code mort)

### Métriques qualitatives
- **Lisibilité** : Nouveau dev comprend architecture en <2h
- **Maintenabilité** : Ajout nouvelle plateforme en <1 jour
- **Robustesse** : Gestion erreurs claire, logs structurés
- **Sécurité** : Credentials jamais loggés, keyring par défaut

---

## 🚨 Pièges à éviter

### 1. Big Bang Rewrite
❌ **Ne pas** tout réécrire from scratch  
✅ **Faire** refactoring incrémental avec tests

### 2. Sur-optimisation prématurée
❌ **Ne pas** remplacer Pandas par Polars immédiatement  
✅ **Faire** format léger d'abord, optimiser si besoin mesuré

### 3. Abstraction excessive
❌ **Ne pas** créer 10 niveaux de classes "au cas où"  
✅ **Faire** 3 niveaux max, composition si besoin

### 4. Ignorer les tests
❌ **Ne pas** refactorer sans tests  
✅ **Faire** tests d'abord, puis refactoring

### 5. Migrer de technologie sans raison
❌ **Ne pas** réécrire en JavaScript/TypeScript  
✅ **Faire** améliorer architecture Python existante

---

## 📚 Ressources

### Documentation à créer
- `CONTRIBUTING.md` : Guide pour contributeurs
- `ARCHITECTURE.md` : Schémas et explications détaillées
- `API.md` : Documentation des classes/méthodes publiques
- `MIGRATION_GUIDE.md` : Guide de migration Pandas → TableData

### Outils à intégrer
- **pre-commit** : Hooks pour formatage (black, isort, mypy)
- **tox** : Tests multi-versions Python
- **GitHub Actions** : CI/CD automatique
- **Codecov** : Suivi de la couverture

### Lectures recommandées
- "Refactoring" (Martin Fowler) : Techniques de refactoring
- "Clean Architecture" (Robert Martin) : Principes d'architecture
- Polars documentation : Alternative moderne à Pandas
- Pydantic documentation : Validation de données

---

## 🎬 Conclusion

### Verdict : REFACTORER, ne pas réécrire

Le projet TableClone a une **base solide** mais souffre de **sur-ingénierie**. Les connaissances métier (normalisations, quirks de chaque plateforme) sont précieuses et doivent être préservées.

### Stratégie recommandée

1. **Court terme** : Stabiliser avec tests
2. **Moyen terme** : Simplifier architecture (TableData, comparator)
3. **Long terme** : Améliorer observabilité et sécurité

**Durée estimée** : 6 mois de travail progressif  
**Résultat** : Code 50% plus simple, aussi performant, mieux testé

### Premier commit recommandé

```bash
# Créer branche de refactoring
git checkout -b refactor/simplify-architecture

# Phase 1.1 : Tests
mkdir -p tests/integration
touch tests/integration/test_airtable_sync.py
# ... écrire premier test

# Commit
git add tests/
git commit -m "feat: add integration tests for Airtable sync

- Create test infrastructure
- Add first Airtable → SQLite sync test
- Setup pytest configuration

Part of refactoring plan (Phase 1, Week 1)"
```

---

**Document maintenu par** : Équipe TableClone  
**Dernière mise à jour** : Octobre 2025  
**Version** : 1.0
