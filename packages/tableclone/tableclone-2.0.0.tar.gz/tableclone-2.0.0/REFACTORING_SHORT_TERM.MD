État actuel

  ✅ Airtable : get_table_schema() implémenté (lit depuis l'API)❌ PostgreSQL : NotImplementedError❌ SQLite : NotImplementedError✅ Fallback : table_schema_from_df() existe mais appelé après sanitize

  Proposition d'implémentation

  1. PostgreSQL : Lire depuis information_schema

  # tableclone/platforms/postgresql.py

  def get_table_schema(self) -> list[Field]:
      """
      Returns a list of Tableclone Fields by querying PostgreSQL information_schema
      """
      self.log("Fetching table schema from information_schema")

      statement = f"""
          SELECT column_name, data_type, udt_name
          FROM information_schema.columns
          WHERE table_schema = '{self.schema}'
          AND table_name = '{self.table}'
          ORDER BY ordinal_position
      """

      rows = self.platform.sql_query(statement)

      tableclone_schema = []
      for row in rows:
          column_name = row[0]
          data_type = row[1]  # Ex: "integer", "text", "timestamp without time zone"

          # Mapper PostgreSQL types → FieldTypes
          pg_type_mapping = {
              "integer": FieldTypes.INTEGER,
              "bigint": FieldTypes.INTEGER,
              "smallint": FieldTypes.INTEGER,
              "numeric": FieldTypes.NUMBER,
              "real": FieldTypes.NUMBER,
              "double precision": FieldTypes.NUMBER,
              "text": FieldTypes.STRING,
              "character varying": FieldTypes.STRING,
              "character": FieldTypes.STRING,
              "boolean": FieldTypes.BOOLEAN,
              "date": FieldTypes.DATE,
              "timestamp without time zone": FieldTypes.DATETIME,
              "timestamp with time zone": FieldTypes.DATETIME,
              # Ajouter plus si besoin
          }

          generic_type = pg_type_mapping.get(data_type, FieldTypes.STRING)  # Fallback STRING

          field = Field(
              platform=self.platform,
              field_name=column_name,
              field_specific_type=data_type,  # "integer", "text", etc.
          )
          # Override generic_type (car Field.__init__ essaie de mapper via FIELD_MAPPING)
          field.generic_type = generic_type

          tableclone_schema.append(field)

      return tableclone_schema

  2. SQLite : Lire depuis PRAGMA table_info

  # tableclone/platforms/sqlite.py

  def get_table_schema(self) -> list[Field]:
      """
      Returns a list of Tableclone Fields by querying SQLite PRAGMA table_info
      """
      self.log("Fetching table schema from PRAGMA table_info")

      statement = f'PRAGMA table_info("{self.table}")'
      rows = self.platform.sql_query(statement)

      # PRAGMA table_info returns: (cid, name, type, notnull, dflt_value, pk)
      # Ex: (0, 'id', 'INTEGER', 1, None, 1)

      tableclone_schema = []
      for row in rows:
          column_name = row[1]
          sqlite_type = row[2].upper()  # "INTEGER", "TEXT", "REAL", etc.

          # Mapper SQLite types → FieldTypes
          sqlite_type_mapping = {
              "INTEGER": FieldTypes.INTEGER,
              "INT": FieldTypes.INTEGER,
              "BIGINT": FieldTypes.INTEGER,
              "REAL": FieldTypes.NUMBER,
              "FLOAT": FieldTypes.NUMBER,
              "DOUBLE": FieldTypes.NUMBER,
              "NUMERIC": FieldTypes.NUMBER,
              "TEXT": FieldTypes.STRING,
              "VARCHAR": FieldTypes.STRING,
              "CHAR": FieldTypes.STRING,
              "BOOLEAN": FieldTypes.BOOLEAN,
              "DATE": FieldTypes.DATE,
              "DATETIME": FieldTypes.DATETIME,
              "TIMESTAMP": FieldTypes.DATETIME,
          }

          generic_type = sqlite_type_mapping.get(sqlite_type, FieldTypes.STRING)

          field = Field(
              platform=self.platform,
              field_name=column_name,
              field_specific_type=sqlite_type,
          )
          field.generic_type = generic_type

          tableclone_schema.append(field)

      return tableclone_schema

  3. Modifier get_sanitized_df() : Schema AVANT sanitize

  # tableclone/platforms/abstracts.py

  def get_sanitized_df(
      self, date_normalize=False, modified_after=None
  ) -> pd.DataFrame:
      """
      Uses allowed_columns to filter / reorder the DataFrame
      Sanitize DataFrame for general API compatibility: replace np.nan by None
      """
      df = self.get_all_as_df(modified_after=modified_after)
      self.log(f"{len(df)} records loaded")

      # NOUVEAU : Inférer le schema AVANT sanitize (pendant que types sont corrects)
      try:
          # Essayer de lire depuis l'API
          self._cached_schema = self.get_table_schema()
          self.log(f"Schema loaded from API: {len(self._cached_schema)} fields")
      except NotImplementedError:
          # Fallback : inférer depuis DataFrame AVANT replace NaN → None
          self.log("get_table_schema() not implemented, inferring from DataFrame")
          self._cached_schema = self.table_schema_from_df(df)

      # Maintenant on peut sanitize (même si ça change les types en object)
      df = self.sanitize_df(df, date_normalize=date_normalize)

      if df.index.duplicated().any():
          raise IndexError(f"Duplicated index for {self}")

      return df

  @property
  def schema(self) -> list[Field]:
      """
      Returns cached schema (computed during get_sanitized_df)
      """
      if not hasattr(self, '_cached_schema'):
          # Si schema pas encore chargé, le faire maintenant
          try:
              self._cached_schema = self.get_table_schema()
          except NotImplementedError:
              # Fallback : charger data et inférer
              df = self.get_all_as_df()
              self._cached_schema = self.table_schema_from_df(df)

      return self._cached_schema

  4. Utilisation dans TableSyncTask

  # tableclone/tasking/table_sync_task.py

  def simple_sync(self, columns_mapping: dict):
      # Charger les données (schema sera inféré AVANT sanitize)
      src_df = self.source.get_sanitized_df(date_normalize=True)
      dst_df = self.destination.get_sanitized_df(date_normalize=True)

      # Récupérer les schemas (déjà cachés)
      src_schema = self.source.schema
      dst_schema = self.destination.schema

      # Utiliser le schema pour validation ou conversion
      src_field_types = {f.name: f.generic_type for f in src_schema}

      # Exemple : vérifier qu'on ne mappe pas INTEGER → STRING
      for src_col, dst_col in columns_mapping.items():
          src_type = src_field_types.get(src_col)
          dst_type = next((f.generic_type for f in dst_schema if f.name == dst_col), None)

          if src_type and dst_type and src_type != dst_type:
              self.log(
                  f"Warning: Mapping {src_col} ({src_type}) → {dst_col} ({dst_type})",
                  level="warning"
              )

      # Le reste comme avant
      # ...

  Avantages de cette approche

  ✅ Types corrects : Schema lu AVANT replace({np.nan: None})✅ Backward compatible : Fallback sur table_schema_from_df() si API pas dispo✅ Cachage : Schema calculé 1 fois, réutilisé✅ Validation : Permet de détecter les mappings incompatibles✅ Future-proof : Base pour migration Polars
  future
