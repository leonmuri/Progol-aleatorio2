import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
from typing import List, Dict, Optional
from datetime import datetime

class QuinielaDatabase:
    """Clase para manejar la persistencia de quinielas en PostgreSQL"""
    
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        self.db_available = self.database_url is not None
        if self.db_available:
            self._init_database()
    
    def _get_connection(self):
        """Obtiene una conexión a la base de datos"""
        return psycopg2.connect(self.database_url)
    
    def _init_database(self):
        """Inicializa las tablas necesarias en la base de datos"""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            # Crear tabla de quinielas
            cur.execute("""
                CREATE TABLE IF NOT EXISTS quinielas (
                    id SERIAL PRIMARY KEY,
                    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    num_partidos INTEGER,
                    datos JSONB NOT NULL
                )
            """)
            
            # Crear índice para búsquedas por fecha
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_quinielas_fecha 
                ON quinielas(fecha_generacion DESC)
            """)
            
            conn.commit()
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"Error inicializando base de datos: {e}")
    
    def guardar_quiniela(self, quiniela: List[Dict]) -> Optional[int]:
        """
        Guarda una quiniela en la base de datos
        
        Args:
            quiniela: Lista de predicciones de la quiniela
            
        Returns:
            ID de la quiniela guardada o None si hay error
        """
        if not self.db_available:
            return None
        
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            num_partidos = len(quiniela)
            datos_json = json.dumps(quiniela, ensure_ascii=False)
            
            cur.execute("""
                INSERT INTO quinielas (num_partidos, datos)
                VALUES (%s, %s)
                RETURNING id
            """, (num_partidos, datos_json))
            
            quiniela_id = cur.fetchone()[0]
            
            conn.commit()
            cur.close()
            conn.close()
            
            return quiniela_id
            
        except Exception as e:
            print(f"Error guardando quiniela: {e}")
            return None
    
    def obtener_quinielas(self, limite: int = 50) -> List[Dict]:
        """
        Obtiene las últimas quinielas guardadas
        
        Args:
            limite: Número máximo de quinielas a recuperar
            
        Returns:
            Lista de quinielas con sus metadatos
        """
        if not self.db_available:
            return []
        
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT id, fecha_generacion, num_partidos, datos
                FROM quinielas
                ORDER BY fecha_generacion DESC
                LIMIT %s
            """, (limite,))
            
            quinielas = []
            for row in cur.fetchall():
                datos = row['datos']
                if isinstance(datos, str):
                    datos = json.loads(datos)
                
                quinielas.append({
                    'id': row['id'],
                    'fecha_generacion': row['fecha_generacion'],
                    'num_partidos': row['num_partidos'],
                    'datos': datos
                })
            
            cur.close()
            conn.close()
            
            return quinielas
            
        except Exception as e:
            print(f"Error obteniendo quinielas: {e}")
            return []
    
    def obtener_quiniela_por_id(self, quiniela_id: int) -> Optional[Dict]:
        """
        Obtiene una quiniela específica por su ID
        
        Args:
            quiniela_id: ID de la quiniela
            
        Returns:
            Diccionario con los datos de la quiniela o None si no existe
        """
        if not self.db_available:
            return None
        
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT id, fecha_generacion, num_partidos, datos
                FROM quinielas
                WHERE id = %s
            """, (quiniela_id,))
            
            row = cur.fetchone()
            
            cur.close()
            conn.close()
            
            if row:
                datos = row['datos']
                if isinstance(datos, str):
                    datos = json.loads(datos)
                
                return {
                    'id': row['id'],
                    'fecha_generacion': row['fecha_generacion'],
                    'num_partidos': row['num_partidos'],
                    'datos': datos
                }
            return None
            
        except Exception as e:
            print(f"Error obteniendo quiniela {quiniela_id}: {e}")
            return None
    
    def eliminar_quiniela(self, quiniela_id: int) -> bool:
        """
        Elimina una quiniela de la base de datos
        
        Args:
            quiniela_id: ID de la quiniela a eliminar
            
        Returns:
            True si se eliminó exitosamente, False en caso contrario
        """
        if not self.db_available:
            return False
        
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute("DELETE FROM quinielas WHERE id = %s", (quiniela_id,))
            
            eliminado = cur.rowcount > 0
            
            conn.commit()
            cur.close()
            conn.close()
            
            return eliminado
            
        except Exception as e:
            print(f"Error eliminando quiniela {quiniela_id}: {e}")
            return False
    
    def obtener_estadisticas(self) -> Dict:
        """
        Obtiene estadísticas generales de las quinielas guardadas
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.db_available:
            return {
                'total_quinielas': 0,
                'primera_quiniela': None,
                'ultima_quiniela': None
            }
        
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Total de quinielas
            cur.execute("SELECT COUNT(*) as total FROM quinielas")
            total = cur.fetchone()['total']
            
            # Fecha de primera y última quiniela
            cur.execute("""
                SELECT 
                    MIN(fecha_generacion) as primera,
                    MAX(fecha_generacion) as ultima
                FROM quinielas
            """)
            fechas = cur.fetchone()
            
            cur.close()
            conn.close()
            
            return {
                'total_quinielas': total,
                'primera_quiniela': fechas['primera'],
                'ultima_quiniela': fechas['ultima']
            }
            
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {
                'total_quinielas': 0,
                'primera_quiniela': None,
                'ultima_quiniela': None
            }
