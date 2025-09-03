#!/usr/bin/env python3
"""
Script para migrar datos de SQLite3 a PostgreSQL
Autor: Script de migracion automatica
Fecha: 2024
"""

import sqlite3
import psycopg2
import logging
from typing import List, Dict, Any, Tuple
import sys
import os
from datetime import datetime

# Configuracion de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SQLiteToPostgreSQLMigrator:
    def __init__(self, sqlite_db_path: str, pg_config: Dict[str, str], exclude_tables: List[str]):
        """
        Inicializa el migrador
        
        Args:
            sqlite_db_path: Ruta al archivo SQLite
            pg_config: Configuración de PostgreSQL
                {
                    'host': 'localhost',
                    'port': '5432',
                    'database': 'nombre_db',
                    'user': 'usuario',
                    'password': 'contraseña'
                }
        """
        self.sqlite_db_path = sqlite_db_path
        self.pg_config = pg_config
        self.exclude_tables = exclude_tables
        self.sqlite_conn = None
        self.pg_conn = None
        
        # Mapeo de tipos SQLite a PostgreSQL
        self.type_mapping = {
            'INTEGER': 'INTEGER',
            'TEXT': 'TEXT',
            'REAL': 'REAL',
            'BLOB': 'BYTEA',
            'NULL': 'TEXT',
            'NUMERIC': 'NUMERIC',
            'BOOLEAN': 'BOOLEAN',
            'DATETIME': 'TIMESTAMP',
            'DATE': 'DATE',
            'TIME': 'TIME'
        }
    
    def connect_databases(self) -> bool:
        """Establece conexiones a ambas bases de datos"""
        try:
            # Conexión a SQLite
            if not os.path.exists(self.sqlite_db_path):
                logger.error(f"El archivo SQLite no existe: {self.sqlite_db_path}")
                return False
            
            self.sqlite_conn = sqlite3.connect(self.sqlite_db_path)
            self.sqlite_conn.row_factory = sqlite3.Row
            logger.info("Conexión a SQLite establecida")
            
            # Conexión a PostgreSQL
            self.pg_conn = psycopg2.connect(**self.pg_config)
            self.pg_conn.autocommit = False
            logger.info("Conexión a PostgreSQL establecida")
            
            return True
            
        except Exception as e:
            logger.error(f"Error al conectar a las bases de datos: {e}")
            return False
    
    def get_sqlite_tables(self) -> List[str]:
        """Obtiene la lista de tablas de SQLite"""
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = [row[0] for row in cursor.fetchall() if row[0] not in self.exclude_tables]
            logger.info(f"Tablas encontradas en SQLite: {tables}")
            return tables
        except Exception as e:
            logger.error(f"Error al obtener tablas de SQLite: {e}")
            return []
    
    def get_table_schema(self, table_name: str) -> List[Tuple[str, str, bool]]:
        """
        Obtiene el esquema de una tabla de SQLite
        
        Returns:
            Lista de tuplas (nombre_columna, tipo, es_primary_key)
        """
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(f"PRAGMA table_info(`{table_name}`)")
            columns = []
            
            for row in cursor.fetchall():
                col_name = row[1]
                col_type = row[2].upper()
                is_pk = bool(row[5])
                
                # Mapear tipo SQLite a PostgreSQL
                pg_type = self.detect_column_type(table_name, col_name, col_type)
                columns.append((col_name, pg_type, is_pk))
            
            logger.info(f"Esquema de {table_name}: {columns}")
            return columns
            
        except Exception as e:
            logger.error(f"Error al obtener esquema de {table_name}: {e}")
            return []
    
    def detect_column_type(self, table_name: str, col_name: str, declared_type: str) -> str:
        """
        Detecta el tipo apropiado para PostgreSQL basándose en nombre y contenido
        
        Args:
            table_name: Nombre de la tabla
            col_name: Nombre de la columna  
            declared_type: Tipo declarado en SQLite
            
        Returns:
            Tipo apropiado para PostgreSQL
        """
        # Mapeo básico
        pg_type = self.type_mapping.get(declared_type, 'TEXT')
        
        # Detectar campos boolean por nombre de columna
        boolean_indicators = [
            'is_', 'has_', 'can_', 'should_', 'will_', 'was_', 'were_',
            'active', 'enabled', 'disabled', 'visible', 'hidden',
            'public', 'private', 'deleted', 'archived', 'published',
            'verified', 'approved', 'confirmed', 'completed', 'finished'
        ]
        
        col_lower = col_name.lower()
        
        # Si el nombre sugiere boolean y el tipo es INTEGER, probablemente es boolean
        if declared_type == 'INTEGER':
            for indicator in boolean_indicators:
                if col_lower.startswith(indicator) or col_lower.endswith(indicator):
                    # Verificar valores reales en la tabla para confirmar
                    if self.is_boolean_column(table_name, col_name):
                        logger.info(f"Detectado campo boolean: {table_name}.{col_name}")
                        return 'BOOLEAN'
        
        return pg_type
    
    def is_boolean_column(self, table_name: str, col_name: str) -> bool:
        """
        Verifica si una columna contiene solo valores boolean (0, 1, NULL)
        
        Returns:
            True si parece ser una columna boolean
        """
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(f'''
                SELECT DISTINCT "{col_name}" 
                FROM "{table_name}" 
                WHERE "{col_name}" IS NOT NULL
            ''')
            
            unique_values = [row[0] for row in cursor.fetchall()]
            
            # Si solo contiene 0, 1 (y posiblemente NULL), es boolean
            boolean_values = {0, 1, '0', '1', True, False}
            return all(value in boolean_values for value in unique_values)
            
        except Exception:
            return False
        
    def get_foreign_keys(self, table_name: str) -> List[Tuple[str, str, str]]:
        """
        Obtiene las foreign keys de una tabla
        
        Returns:
            Lista de tuplas (columna_local, tabla_referenciada, columna_referenciada)
        """
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(f"PRAGMA foreign_key_list(`{table_name}`)")
            foreign_keys = []
            
            for row in cursor.fetchall():
                local_col = row[3]      # from column
                ref_table = row[2]      # table
                ref_col = row[4]        # to column
                foreign_keys.append((local_col, ref_table, ref_col))
            
            if foreign_keys:
                logger.info(f"Foreign keys en {table_name}: {foreign_keys}")
            
            return foreign_keys
            
        except Exception as e:
            logger.error(f"Error al obtener foreign keys de {table_name}: {e}")
            return []
    
    def build_dependency_graph(self, tables: List[str]) -> Dict[str, List[str]]:
        """
        Construye un grafo de dependencias basado en foreign keys
        
        Returns:
            Diccionario donde cada clave es una tabla y el valor es la lista 
            de tablas de las que depende
        """
        dependencies = {table: [] for table in tables}
        
        for table in tables:
            foreign_keys = self.get_foreign_keys(table)
            for _, ref_table, _ in foreign_keys:
                if ref_table in tables and ref_table != table:
                    dependencies[table].append(ref_table)
        
        logger.info(f"Grafo de dependencias: {dependencies}")
        return dependencies
    
    def topological_sort(self, dependencies: Dict[str, List[str]]) -> List[str]:
        """
        Ordena las tablas usando ordenamiento topológico para respetar dependencias
        
        Returns:
            Lista de tablas ordenadas por dependencias
        """
        # Crear una copia para no modificar el original
        deps_copy = {k: v[:] for k, v in dependencies.items()}
        
        # Algoritmo de Kahn para ordenamiento topológico
        in_degree = {table: 0 for table in deps_copy.keys()}
        
        # Calcular grado de entrada para cada tabla
        for table in deps_copy:
            for dep in deps_copy[table]:
                in_degree[table] += 1
        
        # Cola con tablas sin dependencias
        queue = [table for table, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current_table = queue.pop(0)
            result.append(current_table)
            
            # Remover aristas salientes
            for table in deps_copy:
                if current_table in deps_copy[table]:
                    deps_copy[table].remove(current_table)
                    in_degree[table] -= 1
                    if in_degree[table] == 0:
                        queue.append(table)
        
        # Verificar ciclos
        if len(result) != len(in_degree):
            remaining = [t for t in in_degree.keys() if t not in result]
            logger.warning(f"Posibles dependencias circulares detectadas en: {remaining}")
            # Agregar tablas restantes al final
            result.extend(remaining)
        
        logger.info(f"Orden de creación de tablas: {result}")
        return result
    
    def create_postgresql_table(self, table_name: str, schema: List[Tuple[str, str, bool]]) -> bool:
        """Crea una tabla en PostgreSQL basada en el esquema de SQLite (SIN foreign keys)"""
        try:
            cursor = self.pg_conn.cursor()
            
            # Construir SQL de creación de tabla
            columns_sql = []
            primary_keys = []
            
            for col_name, col_type, is_pk in schema:
                column_def = f'"{col_name}" {col_type}'
                columns_sql.append(column_def)
                
                if is_pk:
                    primary_keys.append(f'"{col_name}"')
            
            # Agregar PRIMARY KEY si existe
            if primary_keys:
                columns_sql.append(f"PRIMARY KEY ({', '.join(primary_keys)})")
            
            create_sql = f'''
                CREATE TABLE IF NOT EXISTS "{table_name}" (
                    {', '.join(columns_sql)}
                )
            '''
            
            cursor.execute(create_sql)
            logger.info(f"Tabla {table_name} creada en PostgreSQL (sin constraints)")
            return True
            
        except Exception as e:
            logger.error(f"Error al crear tabla {table_name} en PostgreSQL: {e}")
            return False
    
    def add_foreign_keys(self, table_name: str) -> bool:
        """Agrega las foreign keys a una tabla después de que todas las tablas existen"""
        try:
            foreign_keys = self.get_foreign_keys(table_name)
            if not foreign_keys:
                return True
            
            cursor = self.pg_conn.cursor()
            
            for i, (local_col, ref_table, ref_col) in enumerate(foreign_keys):
                constraint_name = f"fk_{table_name}_{local_col}_{i}"
                
                alter_sql = f'''
                    ALTER TABLE "{table_name}" 
                    ADD CONSTRAINT "{constraint_name}" 
                    FOREIGN KEY ("{local_col}") 
                    REFERENCES "{ref_table}" ("{ref_col}")
                '''
                
                try:
                    cursor.execute(alter_sql)
                    logger.info(f"Foreign key agregada: {table_name}.{local_col} -> {ref_table}.{ref_col}")
                except Exception as e:
                    logger.warning(f"No se pudo agregar FK {constraint_name}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error al agregar foreign keys a {table_name}: {e}")
            return False
    
    def migrate_table_data(self, table_name: str) -> bool:
        """Migra los datos de una tabla de SQLite a PostgreSQL"""
        try:
            # Obtener datos de SQLite
            sqlite_cursor = self.sqlite_conn.cursor()
            sqlite_cursor.execute(f'SELECT * FROM "{table_name}"')
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                logger.info(f"La tabla {table_name} está vacía")
                return True
            
            # Obtener nombres de columnas
            column_names = [description[0] for description in sqlite_cursor.description]
            schema = self.get_table_schema(table_name=table_name)
            
            # Preparar inserción en PostgreSQL
            pg_cursor = self.pg_conn.cursor()
            
            # Construir SQL de inserción
            columns_str = ', '.join(f'"{col}"' for col in column_names)
            placeholders = ', '.join(['%s'] * len(column_names))
            insert_sql = f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({placeholders})'
            
            # Insertar datos por lotes
            batch_size = 100000
            total_rows = len(rows)
            pg_cursor.execute(f'DELETE FROM public.{table_name} WHERE {"id>0" if "id" in column_names else "1=1"};')
            for i in range(0, total_rows, batch_size):
                batch = rows[i:i + batch_size]
                batch_data = [tuple([(bool(row[i]) if schema[i][1] == 'BOOLEAN' else row[i]) for i in range(len(row))]) for row in batch]
                
                pg_cursor.executemany(insert_sql, batch_data)
                logger.info(f"Insertadas {len(batch)} filas en {table_name} ({i + len(batch)}/{total_rows})")
            
            logger.info(f"Migración de {table_name} completada: {total_rows} filas")
            return True
            
        except Exception as e:
            logger.error(f"Error al migrar datos de {table_name}: {e}")
            return False
    
    def migrate_all_tables(self) -> bool:
        """Migra todas las tablas de SQLite a PostgreSQL respetando dependencias"""
        try:
            tables = self.get_sqlite_tables()
            if not tables:
                logger.warning("No se encontraron tablas para migrar")
                return True
            
            # FASE 1: Analizar dependencias y ordenar tablas
            logger.info("=== FASE 1: Analizando dependencias ===")
            dependencies = self.build_dependency_graph(tables)
            ordered_tables = self.topological_sort(dependencies)
            
            # FASE 2: Crear todas las tablas SIN foreign keys
            logger.info("=== FASE 2: Creando estructura de tablas ===")
            created_tables = []
            
            for table_name in ordered_tables:
                logger.info(f"Creando estructura de tabla: {table_name}")
                
                schema = self.get_table_schema(table_name)
                if not schema:
                    logger.error(f"No se pudo obtener esquema de {table_name}")
                    continue
                
                if self.create_postgresql_table(table_name, schema):
                    created_tables.append(table_name)
                else:
                    logger.error(f"No se pudo crear tabla {table_name}")
            
            # Commit después de crear todas las estructuras
            self.pg_conn.commit()
            logger.info(f"Estructuras creadas: {len(created_tables)} tablas")
            
            # FASE 3: Migrar datos
            logger.info("=== FASE 3: Migrando datos ===")
            migrated_tables = []
            
            for table_name in ordered_tables:
                if table_name not in created_tables:
                    continue
                    
                logger.info(f"Migrando datos de tabla: {table_name}")
                
                if self.migrate_table_data(table_name):
                    migrated_tables.append(table_name)
                    self.pg_conn.commit()
                    logger.info(f"OK Datos de {table_name} migrados exitosamente")
                else:
                    logger.error(f"ERROR Error en migración de datos de {table_name}")
                    self.pg_conn.rollback()
            
            # FASE 4: Agregar foreign keys
            logger.info("=== FASE 4: Agregando Foreign Keys ===")
            fk_success = 0
            
            for table_name in ordered_tables:
                if table_name not in migrated_tables:
                    continue
                
                if self.add_foreign_keys(table_name):
                    fk_success += 1
            
            # Commit final
            self.pg_conn.commit()
            
            logger.info(f"""
=== RESUMEN DE MIGRACIÓN ===
Tablas estructuradas: {len(created_tables)}/{len(tables)}
Tablas con datos: {len(migrated_tables)}/{len(tables)}
Foreign keys: {fk_success}/{len(migrated_tables)}
            """)
            
            return len(migrated_tables) == len(tables)
            
        except Exception as e:
            logger.error(f"Error en migración general: {e}")
            self.pg_conn.rollback()
            return False
    
    def close_connections(self):
        """Cierra las conexiones a las bases de datos"""
        if self.sqlite_conn:
            self.sqlite_conn.close()
            logger.info("Conexión SQLite cerrada")
        
        if self.pg_conn:
            self.pg_conn.close()
            logger.info("Conexión PostgreSQL cerrada")
    
    def run_migration(self) -> bool:
        """Ejecuta todo el proceso de migración"""
        logger.info("=== INICIANDO MIGRACIÓN SQLite3 -> PostgreSQL ===")
        start_time = datetime.now()
        
        try:
            # Conectar bases de datos
            if not self.connect_databases():
                return False
            
            # Ejecutar migración
            success = self.migrate_all_tables()
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            if success:
                logger.info(f"SUCCESS MIGRACIÓN COMPLETADA EXITOSAMENTE en {duration}")
            else:
                logger.error(f"ERROR MIGRACIÓN FALLÓ después de {duration}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error crítico en migración: {e}")
            return False
        
        finally:
            self.close_connections()


            
if __name__ == "__main__":
    SQLITE_DB_PATH = "../instance/trading_journal.db"

    POSTGRESQL_CONFIG = {
        'host': 'onemade.es',
        'port': '5432', 
        'database': 'trading_journal',
        'user': 'trading_journal_admin',
        'password': '[*OnEmAdE#jOUrnAl3680]'
    }

    EXCLUDE_TABLES = ['alembic_version', 'balance', 'candle', 'error', 'level', 'media', 'setting', 'strategy', 'strategy_condition', 'trade', 'trade_error', 'trade_scoring', 'user', 'watchlist', 'watchlist_condition', 'watchlist_entry', 'watchlist_levels', 'watchlist_scoring']
    
    # Crear migrador y ejecutar
    migrator = SQLiteToPostgreSQLMigrator(sqlite_db_path=SQLITE_DB_PATH, pg_config=POSTGRESQL_CONFIG, exclude_tables=EXCLUDE_TABLES)
    
    try:
        success = migrator.run_migration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Migracion interrumpida por el usuario")
        migrator.close_connections()
        sys.exit(1)