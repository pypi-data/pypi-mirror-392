# Feature Flags: Refactorisation des méthodes abstraites optionnelles

**Date :** 2025-10-28
**Statut :** Proposition pour refactorisation future
**Priorité :** P2 (après stabilisation Phase 1)

---

## Problématique

### Contexte actuel

L'architecture TableClone utilise des classes abstraites (`abstracts.py`) pour définir le contrat que chaque plateforme doit implémenter. Actuellement, deux patterns coexistent :

1. **`@abstractmethod`** : Utilisé pour `insert_query()`, `update_query()`, `upsert_query()`
   - Force TOUTES les plateformes à implémenter
   - Erreur à l'instanciation si non implémenté

2. **`NotImplementedError`** : Utilisé pour `delete_query()`, `make_bulk_delete_body()`
   - N'empêche pas l'instanciation
   - Erreur seulement si appelé

### Le problème

Quand on ajoute une nouvelle fonctionnalité (ex: `delete()`), on doit choisir :

**Option A : `@abstractmethod`**
- ✅ Force l'implémentation explicite
- ✅ Fail fast (erreur à l'instanciation)
- ❌ **CASSE TOUTES LES PLATEFORMES** immédiatement
- ❌ Force à implémenter même si la plateforme ne supporte pas la feature
- ❌ Empêche le rollout progressif

**Option B : `NotImplementedError`**
- ✅ Permet le rollout progressif (plateforme par plateforme)
- ✅ Ne casse pas les plateformes existantes
- ❌ Fail late (erreur au runtime)
- ❌ Contrats implicites
- ❌ Aucune visibilité sur qui supporte quoi

### Cas concrets problématiques

#### Exemple 1 : Delete
- Airtable supporte delete ✅
- SQLite supporte delete ✅
- Excel ne supporte pas delete ❌ (fichier statique)
- Google Sheets read-only ne supporte pas delete ❌

→ Avec `@abstractmethod`, on force Excel à implémenter une méthode qui n'a aucun sens.

#### Exemple 2 : Upsert
- Airtable supporte upsert natif ✅ (`performUpsert` API)
- PostgreSQL supporte upsert natif ✅ (`ON CONFLICT DO UPDATE`)
- Bubble ne supporte pas upsert natif ❌ (1 requête par record)
- SQLite supporte upsert depuis 3.24.0 ✅ (`INSERT ... ON CONFLICT`)

→ Avec `@abstractmethod`, on force Bubble à implémenter un faux upsert.

#### Exemple 3 : Dump DF
- Airtable peut dump (recréer table) ✅
- SQLite peut dump (DROP + CREATE) ✅
- Excel peut dump (overwrite file) ✅
- API read-only ne peut pas dump ❌

→ Feature avancée que peu de plateformes utilisent réellement.

---

## Solution proposée : Feature Flags explicites

### Principe

Utiliser des **class attributes booléens** pour déclarer explicitement les capabilities de chaque plateforme :

```python
class AirtableTable(InsertUpdateUpsertTable):
    # Feature declarations (documentation vivante)
    SUPPORTS_INSERT = True   # Core
    SUPPORTS_UPDATE = True   # Core
    SUPPORTS_UPSERT = True   # ✅ Airtable a l'API performUpsert
    SUPPORTS_DELETE = True   # ✅ Airtable a l'API DELETE
    SUPPORTS_DUMP = True     # ✅ Airtable peut recréer une table
```

### Règle de décision

**Utiliser `@abstractmethod` SI :**
- La fonctionnalité est **core** (100% des plateformes doivent l'avoir)
- Exemples : `insert_query()`, `update_query()`, `get_bulk_raw_data()`

**Utiliser `NotImplementedError + Feature Flag` SI :**
- La fonctionnalité est **optionnelle** (<100% des plateformes)
- Exemples : `delete_query()`, `upsert_query()`, `dump_df()`

---

## Architecture cible

### 1. Définir les Feature Flags dans la classe abstraite

**Fichier :** `tableclone/platforms/abstracts.py`

```python
class InsertUpdateUpsertTable(Table):
    """
    Base class for tables supporting bulk operations.

    FEATURE FLAGS:
    Subclasses should override these to declare their capabilities.
    """
    # ========================================
    # CORE FEATURES (obligatoires)
    # ========================================
    SUPPORTS_INSERT = True   # All platforms must support insert
    SUPPORTS_UPDATE = True   # All platforms must support update
    SUPPORTS_READ = True     # All platforms must support read

    # ========================================
    # OPTIONAL FEATURES (plateformes spécifiques)
    # ========================================
    SUPPORTS_UPSERT = False  # Native upsert (INSERT ... ON CONFLICT)
    SUPPORTS_DELETE = False  # Deletion operations
    SUPPORTS_DUMP = False    # Full table recreation
    SUPPORTS_SCHEMA_MIGRATION = False  # ALTER TABLE operations
    SUPPORTS_TRANSACTIONS = False  # BEGIN/COMMIT/ROLLBACK

    # ========================================
    # CORE METHODS → @abstractmethod
    # ========================================
    @abstractmethod
    def insert_query(self, body):
        """Insert records (REQUIRED for all platforms)"""
        self.log("Inserting items")

    @abstractmethod
    def update_query(self, body):
        """Update records (REQUIRED for all platforms)"""
        self.log("Updating items")

    # ========================================
    # OPTIONAL METHODS → NotImplementedError
    # ========================================
    def upsert_query(self, body):
        """
        Upsert records (OPTIONAL - check SUPPORTS_UPSERT)

        Only implement if platform has native upsert support.
        Otherwise, use insert + update fallback.
        """
        self.log("Upserting items")
        if not self.SUPPORTS_UPSERT:
            raise NotSupportedError(
                f"{self.PLATFORM} does not support native upsert. "
                f"Use insert() + update() instead."
            )
        raise NotImplementedError(
            f"upsert_query() not implemented for {self.PLATFORM}"
        )

    def delete_query(self, body):
        """
        Delete records (OPTIONAL - check SUPPORTS_DELETE)

        Only implement if platform supports deletion.
        """
        self.log("Deleting items")
        if not self.SUPPORTS_DELETE:
            raise NotSupportedError(
                f"{self.PLATFORM} does not support deletion"
            )
        raise NotImplementedError(
            f"delete_query() not implemented for {self.PLATFORM}"
        )

    def dump_df(self, df):
        """
        Full table recreation (OPTIONAL - check SUPPORTS_DUMP)

        Replaces entire table contents with DataFrame.
        """
        self.log("Dumping dataframe")
        if not self.SUPPORTS_DUMP:
            raise NotSupportedError(
                f"{self.PLATFORM} does not support dump operations"
            )
        raise NotImplementedError(
            f"dump_df() not implemented for {self.PLATFORM}"
        )

    # ========================================
    # PUBLIC API (avec vérification feature flags)
    # ========================================
    def delete(self, ids):
        """
        Delete records by IDs

        Raises:
            NotSupportedError: If platform doesn't support deletion
        """
        if not self.SUPPORTS_DELETE:
            supported_platforms = self._get_platforms_with_feature('SUPPORTS_DELETE')
            raise NotSupportedError(
                f"Deletion not supported for {self.PLATFORM}. "
                f"Supported platforms: {', '.join(supported_platforms)}"
            )

        # Convert to list if needed
        if not isinstance(ids, list):
            ids = list(ids)

        self.log(f"Deleting {len(ids)} items from Table {self}")
        for bulk_ids in self.iter_bulk_delete(ids):
            body_ = self.make_bulk_delete_body(bulk_ids)
            self.log("DELETE DATA\n" + str(body_), level="debug")
            self.delete_query(body_)

    # ========================================
    # HELPER METHODS
    # ========================================
    @classmethod
    def _get_platforms_with_feature(cls, feature_name):
        """
        List all platforms that support a specific feature

        Args:
            feature_name: Name of the feature flag (e.g., 'SUPPORTS_DELETE')

        Returns:
            List of platform names that support the feature
        """
        from .factory import TABLES
        return [
            name for name, table_class in TABLES.items()
            if getattr(table_class, feature_name, False)
        ]

    @classmethod
    def get_supported_features(cls):
        """
        Get list of features supported by this platform

        Returns:
            Dict mapping feature names to boolean support status
        """
        return {
            feature: getattr(cls, feature)
            for feature in dir(cls)
            if feature.startswith('SUPPORTS_')
        }
```

### 2. Déclarer les features dans chaque plateforme

**Fichier :** `tableclone/platforms/airtable.py`

```python
class AirtableTable(PaginatedTable, InsertUpdateUpsertTable):
    PLATFORM = "airtable"

    # ========================================
    # FEATURE DECLARATIONS
    # ========================================
    SUPPORTS_INSERT = True
    SUPPORTS_UPDATE = True
    SUPPORTS_UPSERT = True   # ✅ Airtable API has performUpsert
    SUPPORTS_DELETE = True   # ✅ Airtable API has DELETE
    SUPPORTS_DUMP = False    # ❌ Cannot recreate table via API
    SUPPORTS_SCHEMA_MIGRATION = False  # ❌ Manual only
    SUPPORTS_TRANSACTIONS = False  # ❌ HTTP API, no transactions

    # ... implementation

    def upsert_query(self, body):
        """Implemented because SUPPORTS_UPSERT = True"""
        self.log("Upserting items")
        self.platform.patch(self.update_endpoint, json=body)

    def delete_query(self, body):
        """Implemented because SUPPORTS_DELETE = True"""
        self.log("Deleting items")
        params = {"records[]": body}
        self.platform.delete(self.delete_endpoint, params=params)
```

**Fichier :** `tableclone/platforms/sqlite.py`

```python
class SqliteTable(Table, InsertUpdateUpsertTable):
    PLATFORM = "sqlite"

    # ========================================
    # FEATURE DECLARATIONS
    # ========================================
    SUPPORTS_INSERT = True
    SUPPORTS_UPDATE = True
    SUPPORTS_UPSERT = True   # ✅ SQLite 3.24+ has INSERT ... ON CONFLICT
    SUPPORTS_DELETE = True   # ✅ SQL DELETE statement
    SUPPORTS_DUMP = True     # ✅ Can DROP + CREATE table
    SUPPORTS_SCHEMA_MIGRATION = True  # ✅ ALTER TABLE
    SUPPORTS_TRANSACTIONS = True  # ✅ BEGIN/COMMIT/ROLLBACK

    # ... implementation

    def delete_query(self, body):
        """Implemented because SUPPORTS_DELETE = True"""
        self.log("Deleting items")
        # body est une liste de SQL statements DELETE
        for statement in body:
            self.execute_query(statement)
```

**Fichier :** `tableclone/platforms/excel_file.py`

```python
class ExcelFileTable(Table, InsertUpdateUpsertTable):
    PLATFORM = "excel"

    # ========================================
    # FEATURE DECLARATIONS
    # ========================================
    SUPPORTS_INSERT = True   # ✅ Append rows
    SUPPORTS_UPDATE = True   # ✅ Update rows by index
    SUPPORTS_UPSERT = False  # ❌ No native upsert concept
    SUPPORTS_DELETE = False  # ❌ File-based, complex to delete rows
    SUPPORTS_DUMP = True     # ✅ Can overwrite entire file
    SUPPORTS_SCHEMA_MIGRATION = False  # ❌ No schema concept
    SUPPORTS_TRANSACTIONS = False  # ❌ File-based

    # ... implementation

    # Pas d'implémentation de delete_query (SUPPORTS_DELETE = False)
    # Pas d'implémentation de upsert_query (SUPPORTS_UPSERT = False)
```

### 3. Créer une exception custom

**Fichier :** `tableclone/utils.py`

```python
class NotSupportedError(Exception):
    """
    Raised when a platform doesn't support a specific feature.

    This is different from NotImplementedError:
    - NotSupportedError: Feature is impossible on this platform
    - NotImplementedError: Feature is possible but not coded yet
    """
    pass
```

### 4. Ajouter un helper dans factory

**Fichier :** `tableclone/platforms/factory.py`

```python
def get_platform_capabilities(platform_name: str) -> dict:
    """
    Get the feature flags for a specific platform

    Args:
        platform_name: Name of the platform (e.g., "airtable", "sqlite")

    Returns:
        Dict of feature flags and their values

    Example:
        >>> get_platform_capabilities("airtable")
        {
            'SUPPORTS_INSERT': True,
            'SUPPORTS_UPDATE': True,
            'SUPPORTS_UPSERT': True,
            'SUPPORTS_DELETE': True,
            'SUPPORTS_DUMP': False,
            ...
        }
    """
    if platform_name not in TABLES:
        raise ValueError(f"Unknown platform: {platform_name}")

    table_class = TABLES[platform_name]
    return table_class.get_supported_features()


def list_platforms_with_feature(feature_name: str) -> list[str]:
    """
    List all platforms that support a specific feature

    Args:
        feature_name: Name of the feature (e.g., "SUPPORTS_DELETE")

    Returns:
        List of platform names

    Example:
        >>> list_platforms_with_feature("SUPPORTS_DELETE")
        ['airtable', 'sqlite', 'postgresql', 'bubble']
    """
    return [
        name for name, table_class in TABLES.items()
        if getattr(table_class, feature_name, False)
    ]
```

---

## Plan d'implémentation

### Phase 1 : Préparation (sans breaking changes)

**Durée estimée :** 2 heures

1. **Ajouter `NotSupportedError` dans `utils.py`**
2. **Ajouter les Feature Flags à toutes les plateformes existantes**
   - Airtable, Bubble, SQLite, PostgreSQL, Excel, BaseRow, etc.
   - Documenter l'état actuel (même si `False`)
3. **Ajouter les helpers dans `factory.py`**
   - `get_platform_capabilities()`
   - `list_platforms_with_feature()`
4. **Ajouter `get_supported_features()` dans `InsertUpdateUpsertTable`**

**Validation :** Tests existants passent, aucun changement de comportement

### Phase 2 : Migration des méthodes optionnelles

**Durée estimée :** 3 heures

1. **Convertir `upsert_query()` de `@abstractmethod` → `NotImplementedError`**
   - Ajouter check `SUPPORTS_UPSERT` dans la méthode abstraite
   - Vérifier que seules les plateformes avec `SUPPORTS_UPSERT = True` l'implémentent

2. **Mettre à jour `delete_query()` (déjà NotImplementedError)**
   - Ajouter check `SUPPORTS_DELETE`
   - Améliorer message d'erreur

3. **Mettre à jour `dump_df()` (déjà NotImplementedError)**
   - Ajouter check `SUPPORTS_DUMP`

4. **Mettre à jour toutes les méthodes publiques** (`delete()`, `upsert()`, `dump_df()`)
   - Vérifier le feature flag AVANT d'appeler la méthode interne
   - Lever `NotSupportedError` avec message explicite

**Validation :**
- Appeler `table.delete()` sur Excel → `NotSupportedError` avec message clair
- Appeler `table.delete()` sur Airtable → fonctionne

### Phase 3 : Documentation et tests

**Durée estimée :** 2 heures

1. **Créer tests unitaires pour feature flags**
   ```python
   def test_platform_capabilities():
       assert AirtableTable.SUPPORTS_DELETE == True
       assert ExcelFileTable.SUPPORTS_DELETE == False

   def test_not_supported_error():
       excel_table = table_factory("excel", ...)
       with pytest.raises(NotSupportedError, match="does not support deletion"):
           excel_table.delete(["id1", "id2"])
   ```

2. **Documenter dans `CLAUDE.md`**
   - Section "Feature Flags"
   - Matrice plateforme × feature

3. **Ajouter dans `README.md`**
   - Tableau de compatibilité

---

## Matrice de compatibilité (état cible)

| Platform      | Insert | Update | Upsert | Delete | Dump | Transactions |
|---------------|--------|--------|--------|--------|------|--------------|
| Airtable      | ✅     | ✅     | ✅     | ✅     | ❌   | ❌           |
| Bubble        | ✅     | ✅     | ❌     | ✅     | ❌   | ❌           |
| SQLite        | ✅     | ✅     | ✅     | ✅     | ✅   | ✅           |
| PostgreSQL    | ✅     | ✅     | ✅     | ✅     | ✅   | ✅           |
| Excel         | ✅     | ✅     | ❌     | ❌     | ✅   | ❌           |
| Google Sheets | ✅     | ✅     | ❌     | ✅     | ✅   | ❌           |
| BaseRow       | ✅     | ✅     | ❌     | ✅     | ❌   | ❌           |

---

## Avantages de cette approche

### 1. Documentation vivante
```python
# Avant (implicite)
table.delete([...])  # Est-ce que ça marche ? Aucune idée sans tester

# Après (explicite)
if table.SUPPORTS_DELETE:
    table.delete([...])
else:
    print(f"Delete not supported on {table.PLATFORM}")
```

### 2. Erreurs explicites
```python
# Avant
NotImplementedError: delete_query not implemented

# Après
NotSupportedError: excel does not support deletion.
Supported platforms: airtable, sqlite, postgresql, bubble
```

### 3. Discovery facile
```python
from tableclone.platforms.factory import list_platforms_with_feature

# Quelles plateformes supportent delete ?
platforms = list_platforms_with_feature("SUPPORTS_DELETE")
# → ['airtable', 'sqlite', 'postgresql', 'bubble']

# Quelles features supporte Airtable ?
caps = get_platform_capabilities("airtable")
# → {'SUPPORTS_INSERT': True, 'SUPPORTS_DELETE': True, ...}
```

### 4. Rollout progressif sans breaking changes
```python
# Ajout d'une nouvelle feature "SUPPORTS_BULK_UPLOAD"
# 1. Ajouter le flag (False par défaut) → aucun impact
# 2. Implémenter plateforme par plateforme
# 3. Les anciennes plateformes continuent de fonctionner
```

### 5. Type safety partielle
```python
# Avec mypy/basedpyright
def sync_with_deletion(table: InsertUpdateUpsertTable):
    if not table.SUPPORTS_DELETE:
        reveal_type(table.SUPPORTS_DELETE)  # Revealed type is "Literal[False]"
        raise ValueError("Table must support deletion")

    table.delete([...])  # OK, type checker sait que c'est safe
```

---

## Critères de décision : Core vs Optional

### Une feature est **CORE** (`@abstractmethod`) si :
- ✅ 100% des plateformes actuelles l'implémentent
- ✅ Une plateforme sans cette feature est inutilisable
- ✅ Le contrat de base du projet dépend de cette feature

**Exemples :**
- `insert_query()` → Core (impossible d'avoir une plateforme sans insert)
- `update_query()` → Core (toute plateforme doit pouvoir modifier)
- `get_bulk_raw_data()` → Core (toute plateforme doit pouvoir lire)

### Une feature est **OPTIONAL** (`NotImplementedError + Flag`) si :
- ✅ Moins de 100% des plateformes l'implémentent
- ✅ La plateforme reste utilisable sans cette feature
- ✅ La feature est "nice to have" mais pas critique

**Exemples :**
- `delete_query()` → Optional (Excel, APIs read-only)
- `upsert_query()` → Optional (peut fallback sur insert+update)
- `dump_df()` → Optional (opération avancée peu utilisée)
- `create_table_from_schema()` → Optional (certaines APIs ne le permettent pas)

---

## Exemples d'usage dans le code utilisateur

### Exemple 1 : Vérification avant utilisation
```python
from tableclone.platforms.factory import table_factory

source = table_factory("sqlite", ...)
dest = table_factory("airtable", ...)

# Vérifier si on peut delete
if dest.SUPPORTS_DELETE:
    # Cleanup avant sync
    dest.delete(orphaned_ids)
else:
    print(f"Warning: {dest.PLATFORM} doesn't support deletion. Orphaned records will remain.")
```

### Exemple 2 : Fallback automatique
```python
def smart_upsert(table, df):
    """Upsert with fallback to insert+update"""
    if table.SUPPORTS_UPSERT:
        # Use native upsert (performant)
        table.upsert(df, unique_id_column="id")
    else:
        # Fallback to insert + update (slower but works)
        existing_ids = set(table.get_all_ids())
        df_new = df[~df.index.isin(existing_ids)]
        df_update = df[df.index.isin(existing_ids)]

        if len(df_new) > 0:
            table.insert(df_new)
        if len(df_update) > 0:
            table.update(df_update)
```

### Exemple 3 : Validation de config
```python
from tableclone.platforms.factory import table_factory

def validate_sync_config(config):
    """Validate that source/dest support required features"""
    source = table_factory(config["source"]["platform"], ...)
    dest = table_factory(config["destination"]["platform"], ...)

    # Check delete mode
    if config.get("options", {}).get("delete_mode"):
        if not dest.SUPPORTS_DELETE:
            raise ConfigError(
                f"delete_mode requires destination platform to support deletion. "
                f"{dest.PLATFORM} does not support this feature."
            )

    # Check upsert mode
    if config.get("options", {}).get("upsert_mode"):
        if not dest.SUPPORTS_UPSERT:
            print(f"Warning: {dest.PLATFORM} doesn't support native upsert. "
                  f"Will use insert+update fallback.")
```

---

## Références

### Fichiers à modifier
- `tableclone/utils.py` - Ajouter `NotSupportedError`
- `tableclone/platforms/abstracts.py` - Feature flags + helpers
- `tableclone/platforms/factory.py` - Discovery helpers
- `tableclone/platforms/airtable.py` - Déclarer features
- `tableclone/platforms/bubble.py` - Déclarer features
- `tableclone/platforms/sqlite.py` - Déclarer features
- `tableclone/platforms/postgresql.py` - Déclarer features
- `tableclone/platforms/excel_file.py` - Déclarer features
- (Tous les autres platforms/)
- `CLAUDE.md` - Documenter le système
- `README.md` - Matrice de compatibilité

### Inspiration externe
- Django : `supports_transactions`, `can_return_columns_from_insert`
- SQLAlchemy : `supports_sane_rowcount`, `supports_multivalues_insert`
- Pandas : `_has_complex_internals`, `_can_hold_na`

---

## Notes de migration

### Breaking changes
- ❌ Aucun ! Cette refactorisation est 100% backward compatible
- Les plateformes existantes continuent de fonctionner
- Les nouvelles plateformes bénéficient du système

### Rollback plan
Si problème, revenir à `@abstractmethod` pour les méthodes core est trivial :
```python
# Rollback: supprimer le feature flag check
@abstractmethod  # Remettre decorator
def upsert_query(self, body):
    self.log("Upserting items")
    # Supprimer la ligne suivante
    # if not self.SUPPORTS_UPSERT: raise NotSupportedError(...)
```

---

## Conclusion

Cette refactorisation permet de :
1. **Clarifier le contrat** : Core vs Optional explicite
2. **Améliorer l'UX développeur** : Découverte facile des capabilities
3. **Permettre l'évolution** : Ajout de features sans casser l'existant
4. **Améliorer les erreurs** : Messages explicites avec alternatives

**Prochaine étape suggérée :** Implémenter Phase 1 (Feature Flags sans breaking changes) lors du prochain sprint de refactoring.
