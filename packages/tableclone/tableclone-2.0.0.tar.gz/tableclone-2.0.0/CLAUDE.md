# CLAUDE.md

Guide pour Claude Code (claude.ai/code) lors du travail sur ce repository.

## Project Overview

TableClone est un outil Python de synchronisation de données bidirectionnelle entre plateformes hétérogènes (Airtable, Bubble, PostgreSQL, SQLite, Google Drive, Excel, etc.). Il utilise une couche d'abstraction pour normaliser les opérations de données entre plateformes.

**Note**: Le projet est en phase de stabilisation. Voir `REFACTORING_ANALYSIS.md` pour le plan d'évolution de l'architecture.

## Development Commands

### Installation
```bash
# Configuration moderne avec uv (recommandé)
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

Le projet utilise `pyproject.toml` comme source unique de configuration.

### CLI Usage

```bash
# Synchronisation de table
tableclone sync config.json
tableclone sync '{"source": {...}, "destination": {...}, "options": {...}}'

# Backup complet (container à container)
tableclone full_backup config.json
```

Les variables d'environnement dans les configs sont automatiquement substituées (ex: `"secret_string": "$AIRTABLE_API_KEY"`).

### Testing

- When running pytest, always prefix command with `source .venv/bin/activate && source .env && pytest ...`

```bash
# Tous les tests d'intégration
pytest source .venv/bin/activate && source .env && tests/integration/ -v

# Tests standards (SQLite ↔ PostgreSQL, etc.)
pytest source .venv/bin/activate && source .env && tests/integration/standard/ -v

# Test spécifique avec output détaillé
pytest source .venv/bin/activate && source .env && tests/integration/test_sqlite_to_airtable.py -v -s

# Test spécifique avec log tableclone
source .venv/bin/activate && source .env && pytest source .venv/bin/activate && source .env && tests/integration/test_sqlite_to_airtable.py -v -s --log-cli-level=INFO

# Avec coverage
pytest source .venv/bin/activate && source .env && tests/integration/ --cov=tableclone --cov-report=html
```

**Prérequis tests Airtable** : Variables d'environnement dans `.env`:
```bash
AIRTABLE_API_KEY=your_api_key
AIRTABLE_TEST_BASE_ID=appXXXXXXXXXXXXXX
AIRTABLE_TEST_TABLE_ID=tblXXXXXXXXXXXXXX
```

**Prérequis tests PostgreSQL** : Variables d'environnement dans `.env`:
```bash
TC_PG_USER=your_user
TC_PG_PASSWORD=your_password
TC_PG_DATABASE=tableclone_test
TC_PG_HOST=localhost  # optional, default: localhost
TC_PG_PORT=5432       # optional, default: 5432
```

**Test Scenarios** : Les tests utilisent un framework de scénarios réutilisables :
- `InsertScenario` : Test insert simple (destination vide ← source)
- `UpdateScenario` : Test 2-étapes (insert initial + sync avec modifications)
- `MappingScenario` : Test avec cross-column mapping explicite
- `RoundTripScenario` : Test round-trip (Source1 → Intermediate → Source2)
- `DeleteSimpleScenario` : Test delete avec sélection aléatoire de N items
- `DeleteEmptyScenario` : Test delete sur table vide (edge case)
- `DeleteScenario` : Test delete sync operations (pour tests avancés)

Chaque scénario gère automatiquement les vérifications (inserts, updates, deletes, row counts, mapping, etc.)

**Fixtures de test (table-level)** :
- `airtable_with_test_data` (session-scoped) : Table pré-peuplée pour tests READ
- `airtable_with_modified_data` (session-scoped) : Deuxième table Airtable pré-peuplée avec données modifiées (pour update tests, nécessite TC_AIRTABLE_TEST_TABLE2_ID)
- `clean_airtable_table` (function-scoped) : Table vide pour tests WRITE
- `sqlite_with_sample_data` : SQLite table avec données d'exemple
- `sqlite_with_modified_data` : SQLite table avec données modifiées (pour update tests)
- `postgresql_with_test_data` (session-scoped) : PostgreSQL table avec données d'exemple
- `postgresql_with_modified_data` (session-scoped) : PostgreSQL table avec données modifiées (pour update tests)
- `clean_postgresql_table` : PostgreSQL table vide

**Fixtures de test (container-level)** :
- `airtable_base_with_two_tables` (session-scoped) : Base Airtable avec 2 tables pré-peuplées (nécessite TC_AIRTABLE_TEST_TABLE_ID et TC_AIRTABLE_TEST_TABLE2_ID)
  - Table1 : 15 rows (sample_data)
  - Table2 : 14 rows (modified_sample_data)
  - Retourne dict avec base_id, api_key, table_names, table1, table2
- `excel_temp_file` (function-scoped) : Chemin vers fichier Excel temporaire (auto-cleanup)
- `sqlite_db_temp_path` (function-scoped) : Chemin vers DB SQLite temporaire (auto-cleanup)

Tests indépendants de l'ordre d'exécution

**Structure des tests** :
- `tests/integration/` : Tests ad-hoc et edge cases
- `tests/integration/standard/` : Tests standardisés
  - **Table sync** (3 tests par platform pair) : `test_{source}_to_{destination}.py`
    - Tests : `test_insert`, `test_update`, `test_insert_with_mapping`
  - **Full backup** (2 tests par destination) : `test_full_backup_to_{destination}.py`
    - Tests : `test_airtable_to_{dest}_full_backup`, `test_airtable_to_{dest}_full_backup_filtered`
  - Tous les tests utilisent les scénarios réutilisables

Voir `tests/README.md` pour plus de détails.

## Architecture

### Vue d'ensemble

```
Platform (auth, API calls)
  └─ RestAPIPlatform (plateformes HTTP)

PlatformObject (base)
  ├─ Table (opérations de données)
  │   └─ PaginatedTable (APIs paginées)
  │       └─ InsertUpdateUpsertTable (opérations bulk)
  └─ Container (opérations multi-tables)

TaskInterface (orchestration)
  ├─ TableSyncTask (sync entre deux tables)
  └─ ContainerFullBackupTask (backup de containers)
```

### Factory Pattern

Utiliser les factories pour l'instanciation :

```python
from tableclone.platforms.factory import (
    platform_factory,
    table_factory,
    container_factory
)

platform = platform_factory(platform_name="airtable", ...)
table = table_factory(platform_name="airtable", alias="my_table", ...)
container = container_factory(platform_name="airtable", ...)
```

### Options System

Le système d'options (`utils.py`) gère la validation des configurations :

```python
from tableclone.utils import Option, OptionSet, OptionValues

OPT_MAPPING = Option("mapping", "Column mapping", dict, required=True)
OPTION_SET = OptionSet([OPT_MAPPING, ...])
option_values = OptionValues(OPTION_SET, user_config)
```

Fonctionnalités : validation de type, champs required/optional, détection d'incompatibilités, support enum, valeurs par défaut.

### Configuration Export et Options Dynamiques

Les objets `PlatformObject` (Table, Container) supportent deux méthodes pour gérer les configurations :

**1. `to_config()` - Export de configuration**
```python
table = table_factory("sqlite", alias="my_table", ...)
config = table.to_config()
# Returns: {alias, api_identifier, platform: {platform_root_path, options, secret_string}, options}
```

**2. `with_options()` - Création d'instances avec options modifiées (immutable)**
```python
# Fixture de base
base_table = sqlite_with_sample_data

# Créer des variantes avec différentes options
filtered_table = base_table.with_options(allowed_columns=["id", "name"])
typecast_table = airtable_table.with_options(typecast=True)
```

**Usage dans les tests** :
```python
# Les scénarios appliquent automatiquement les options
scenario = InsertScenario(
    source=sqlite_with_sample_data,
    dest=clean_airtable_table,
    source_table_options={"allowed_columns": ["id", "name", "email"]},
    dest_table_options={"typecast": True},
    ...
)
```

### Test Scenario Pattern

Le framework de scénarios (`tests/integration/scenarios/`) fournit des patterns réutilisables pour tester les syncs :

**Classe de base :** `BaseScenario`
- `_extract_platform_params()` : Extrait les paramètres spécifiques à chaque plateforme
- `_create_table()` : Crée une instance Table via factories
- `_get_dest_records()` : Récupère tous les records de la destination (via `get_all_as_df()`)
- `_get_dest_row_count()` : Compte les rows dans la destination

**Scénarios table-level (TableSyncTask)** :
1. **InsertScenario** : Sync insert simple (destination vide ← source)
   - Vérifie : insert count, no updates, no deletes, row count destination
2. **UpdateScenario** : Sync 2-étapes (insert initial + sync modifications)
   - Sync1: insert initial data
   - Sync2: update + append new rows
   - Vérifie : updated/inserted counts, total rows, data integrity
3. **MappingScenario** : Sync avec mapping explicite (défaut : name ↔ email)
   - Vérifie : insert count, cross-column mapping correctness (avec fixture data)
4. **RoundTripScenario** : Source1 → Intermediate → Source2
   - Vérifie : round-trip data integrity
5. **DeleteScenario** : Delete operations
   - Vérifie : delete count, row count après delete

**Scénarios container-level (ContainerFullBackupTask)** :
6. **FullBackupScenario** : Backup complet container → container (multi-tables)
   - Supporte Airtable → Excel, Airtable → SQLite, etc.
   - Vérifie : fichier/DB créé, nombre de tables, row counts, data integrity
   - Options : table_filter pour backup sélectif

**Utilisation (table-level)** :
```python
from tests.integration.scenarios import InsertScenario

scenario = InsertScenario(
    source=sqlite_with_sample_data,
    dest=clean_postgresql_table,
    config_factory=sync_config_factory,
    sample_data=sample_data,
    source_platform="sqlite",
    dest_platform="postgre",
    source_table_options={"unique_id_column": "id"},
    dest_table_options={"unique_id_column": "id"},
)

result = scenario.execute()
scenario.verify(result)  # Vérifications automatiques
```

**Utilisation (container-level)** :
```python
from tests.integration.scenarios import FullBackupScenario

scenario = FullBackupScenario(
    source_container_info={
        "base_id": "appXXXX",
        "api_key": "keyXXXX",
        "table_names": ["Table1", "Table2"]
    },
    dest_path="/path/to/backup.xlsx",
    source_platform="airtable",
    dest_platform="excel_file",
    container_config_factory=container_config_factory,
    sample_data_by_table={"Table1": sample_data, "Table2": modified_sample_data},
    table_filter=["Table1"],  # Optional: backup seulement Table1
)

result = scenario.execute()
scenario.verify(result, expected_table_count=1, expected_row_counts={"Table1": 15})
```

**Avantages** :
- ✅ **DRY** : Écrit une fois, utilisé partout
- ✅ **Consistency** : Même logique pour tous les platform pairs
- ✅ **Maintainability** : Bug fixes centralisés
- ✅ **Fixture-based** : Pas de hardcoded values, utilise les fixtures

## Structure des fichiers

### Core Infrastructure
- `utils.py` : Système d'options, logging, helpers
- `platforms/abstracts.py` : Classes de base pour toutes les plateformes
- `platforms/factory.py` : Factory pattern pour l'instanciation

### Implémentations de plateformes
- `platforms/airtable.py` : Airtable API
- `platforms/bubble.py` : Bubble.io API
- `platforms/postgresql.py` : PostgreSQL
- `platforms/sqlite.py` : SQLite
- `platforms/excel_file.py` : Fichiers Excel
- `platforms/gdrive.py` : Google Drive
- Autres : BaseRow, KSAAR, TimeTonic

### Orchestration des tâches
- `tasking/abstract_task.py` : Interface de base avec callbacks
- `tasking/table_sync_task.py` : Sync entre deux tables (cas d'usage principal)
- `tasking/full_backup.py` : Backup de containers avec téléchargement d'attachments

### CLI
- `cli_v2.py` : Point d'entrée, chargement de config, substitution env vars

## Opérations CRUD

### Opérations core (requises)
- `insert_query(body)` : Créer des enregistrements
- `update_query(body)` : Mettre à jour des enregistrements
- `get_bulk_raw_data()` : Lire des enregistrements

### Opérations optionnelles (selon plateforme)
- `delete_query(body)` : Supprimer (implémenté : Airtable)
- `upsert_query(body)` : Upsert (implémenté : Airtable, PostgreSQL, SQLite 3.24+)
- `dump_df(df)` : Remplacement complet de table

Les méthodes optionnelles utilisent `NotImplementedError` (pas `@abstractmethod`) pour permettre un déploiement progressif. Voir `FEATURE_FLAGS_REFACTORING.md` pour le design futur.

## Patterns et conventions

### Unique ID Management

**Principe fondamental : L'index du DataFrame contient TOUJOURS l'unique ID**

Toutes les plateformes normalisent leurs données de la même façon :
- **Airtable/Bubble** : L'ID natif de l'API (`record_id`, `_id`) est placé dans l'index du DataFrame
- **PostgreSQL/SQLite** : La colonne spécifiée via `unique_id_column` est placée dans l'index du DataFrame

Les wrappers de plateforme (`get_all_as_df()`) se chargent automatiquement d'indexer correctement le DataFrame.

**Conséquence pour les tests** : Pour récupérer les IDs d'un DataFrame, toujours utiliser `.index.tolist()`, jamais accéder directement à une colonne.

```python
# ✅ Correct (fonctionne pour toutes les plateformes)
df = table.get_all_as_df()
ids = df.index.tolist()

# ❌ Incorrect (spécifique à une plateforme)
ids = df["record_id"].tolist()  # Ne fonctionne que pour Airtable
ids = df["id"].tolist()          # Ne fonctionne que pour SQLite/PostgreSQL
```

**Index naming** : `table_index_name()` génère `tc_{field}` ou utilise un override pour les index de base de données

### Logging

Pattern consistant dans toutes les classes :

```python
from tableclone.utils import get_logger

class MyClass:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def log(self, message, level="info"):
        formated_msg = f"{str(self)} {message}"
        getattr(self.logger, level)(formated_msg)
```

## Développement

### Ajouter une nouvelle plateforme

1. Créer `platforms/my_platform.py` avec classes `MyPlatform` et `MyTable`
2. Implémenter les méthodes core (insert_query, update_query, get_bulk_raw_data)
3. Implémenter optionnellement delete_query, upsert_query
4. Enregistrer dans `platforms/factory.py`
5. Définir le field mapping pour conversion de types
6. Ajouter tests dans `tests/integration/`

Suivre les patterns de `platforms/airtable.py` (implémentation la plus complète).

### Ajouter de nouveaux tests standards

Pour ajouter des tests standards pour une nouvelle platform pair (ex: SQLite ↔ Airtable) :

1. **Créer le fichier test** : `tests/integration/standard/test_{source}_to_{destination}.py`

2. **Implémenter 3 tests standards** :
   ```python
   from tests.integration.scenarios import InsertScenario, UpdateScenario, MappingScenario

   def test_insert(source_fixture, dest_fixture, sync_config_factory, sample_data):
       scenario = InsertScenario(
           source=source_fixture,
           dest=dest_fixture,
           config_factory=sync_config_factory,
           sample_data=sample_data,
           source_platform="sqlite",
           dest_platform="airtable",
           source_table_options={"unique_id_column": "id"},  # Options spécifiques
       )
       result = scenario.execute()
       scenario.verify(result)

   def test_update(initial_source, modified_source, dest_fixture, ...):
       scenario = UpdateScenario(
           initial_source=initial_source,
           modified_source=modified_source,
           dest=dest_fixture,
           ...,
           source_table_options={"allowed_columns": ["id", "name", "email"], "unique_id_column": "id"},
       )
       result = scenario.execute()
       scenario.verify(result, expected_updated_count=12, expected_inserted_count=2)

   def test_insert_with_mapping(source_fixture, dest_fixture, ...):
       scenario = MappingScenario(
           source=source_fixture,
           dest=dest_fixture,
           ...,
           # mapping=None uses default cross-column mapping (name ↔ email)
       )
       result = scenario.execute()
       scenario.verify(result)
   ```

3. **Passer les options** :
   - `source_table_options` : Options spécifiques à la plateforme source (ex: `unique_id_column`)
   - `dest_table_options` : Options spécifiques à la plateforme destination
   - Les scénarios gèrent l'intégration avec TableSyncTask

4. **Mettre à jour** `tests/integration/standard/README.md` avec la nouvelle platform pair

**Convention** :
- Fichier : `test_{source}_to_{destination}.py`
- Fonction : `test_insert()`, `test_update()`, `test_insert_with_mapping()`
- Markers : `@pytest.mark.integration` + `@pytest.mark.{platform}` (ex: `@pytest.mark.airtable`)

### Bonnes pratiques

**DO** :
- ✅ Utiliser les factories pour l'instanciation
- ✅ Utiliser les scénarios pour tous les tests (Insert, Update, Mapping, etc.)
- ✅ Passer les options spécifiques à chaque plateforme (via `source_table_options`, `dest_table_options`)
- ✅ Utiliser les fixtures pour les données de test (pas de hardcoded values)
- ✅ Ajouter des tests pour tout nouveau code
- ✅ Améliorer les docstrings et messages d'erreur
- ✅ Utiliser les variables d'environnement pour les secrets
- ✅ Maintenir la compatibilité avec les configs existantes

**DON'T** :
- ❌ Hardcoder des valeurs de test dans les scénarios
- ❌ Ajouter de la logique métier spécifique à une plateforme dans BaseScenario
- ❌ Hardcoder des secrets
- ❌ Ajouter de nouvelles plateformes avant stabilisation
- ❌ Modifier l'architecture sans tests

### Debugging

- Vérifier les logs (toutes les classes ont `self.log(msg, level)`)
- Utiliser l'option `export_csv` de TableSyncTask
- Vérifier les scopes des fixtures si tests intermittents
- Consulter les fichiers de design (`REFACTORING_ANALYSIS.md`, `FEATURE_FLAGS_REFACTORING.md`)

## Conventions du projet

- **Docstrings** : Google-style (simple et concis)
- **Style** : PEP 8
- **Logging levels** : DEBUG (détails API), INFO (progression), WARNING (récupérable), ERROR (échecs)
- **Secrets** : Variables d'environnement avec `$VAR_NAME` dans les configs
- **Compatibilité** : Maintenir les configs existantes lors de l'ajout de features

## Problèmes connus

1. **Over-abstraction** : 6 niveaux d'héritage (objectif : max 3)
2. **Pandas overuse** : Utilisé pour des opérations simples de dict
3. **Code debt** : ~30-40% de méthodes NotImplementedError jamais appelées
4. **ID management** : 4 approches différentes

Voir `REFACTORING_ANALYSIS.md` pour le plan d'amélioration.

## Status actuel

**Stabilisation Phase 1 (Complété)** :
- ✅ Tests d'intégration SQLite ↔ Airtable (11 tests)
- ✅ Opération delete (infrastructure + Airtable + SQLite + PostgreSQL)
- ✅ Fixtures session-scoped et function-scoped
- ✅ Bug fixes (tables vides, logger init, HTTP errors)
- ✅ Framework de scénarios réutilisables (Insert, Update, Mapping, RoundTrip, Delete)
- ✅ Tests standardisés PostgreSQL (SQLite ↔ PostgreSQL, 3 tests par direction)
- ✅ Tests standardisés Airtable (SQLite ↔ Airtable, 3 tests par direction, fixture airtable_with_modified_data pour updates)
- ✅ Fixtures PostgreSQL avec données modifiées (postgresql_with_modified_data) pour tests d'update
- ✅ Vérifications automatiques dans BaseScenario (row counts, data verification, mapping)
- ✅ Suppression du code dupliqué (tests réduits de ~40%)

**Phase 2 (Complété)** :
- ✅ Tests delete standardisés : `tests/integration/standard/test_delete.py` (6 tests)
  - SQLite : `test_sqlite_delete`, `test_sqlite_delete_empty`
  - PostgreSQL : `test_postgresql_delete`, `test_postgresql_delete_empty`
  - Airtable : `test_airtable_delete`, `test_airtable_delete_empty`
- ✅ Scénarios delete réutilisables : `DeleteSimpleScenario`, `DeleteEmptyScenario`
- ✅ Homogénéisation des fixtures : Toutes retournent des instances Table (plus de tuples)
- ✅ Gestion des secrets centralisée dans `sync_config_factory`
- ✅ Fix `Platform.secret_string` stocké pour réutilisation
- ✅ Documentation du principe d'indexation (`.index` contient toujours l'unique ID)
- ✅ Total : 18 tests standards (12 sync + 6 delete)

**Prochaines priorités** :
- Phase 3 : Ajouter tests standards pour autres platform pairs (PostgreSQL ↔ Airtable, etc.)
- Phase 3 : Ajouter tests pour edge cases (`tests/integration/custom/`)
- Phase 4 : Implémenter Excel export tests (ContainerFullBackupTask)
- Phase 4 : Documenter matrice de capacités des plateformes
