import random
from typing import List, Dict

class QuinielaGenerator:
    """Clase para generar quinielas aleatorias de Progol"""
    
    def __init__(self):
        self.predicciones = {
            'Local': {'codigo': '1', 'simbolo': '🏠'},
            'Empate': {'codigo': 'X', 'simbolo': '🤝'},
            'Visitante': {'codigo': '2', 'simbolo': '✈️'}
        }
    
    def generar_quinielas(self, partidos: List[Dict], cantidad: int = 1) -> List[List[Dict]]:
        """
        Genera una o más quinielas aleatorias basadas en los partidos dados
        
        Args:
            partidos: Lista de diccionarios con información de partidos
            cantidad: Número de quinielas a generar
            
        Returns:
            Lista de quinielas, donde cada quiniela es una lista de predicciones
        """
        if not partidos:
            return []
        
        quinielas = []
        
        for _ in range(cantidad):
            quiniela = self._generar_quiniela_individual(partidos)
            quinielas.append(quiniela)
        
        return quinielas
    
    def _generar_quiniela_individual(self, partidos: List[Dict]) -> List[Dict]:
        """
        Genera una quiniela individual con predicciones aleatorias
        
        Args:
            partidos: Lista de partidos
            
        Returns:
            Lista de diccionarios con predicciones para cada partido
        """
        quiniela = []
        
        for i, partido in enumerate(partidos[:14]):  # Máximo 14 partidos para Progol
            # Generar predicción aleatoria
            prediccion_key = random.choice(list(self.predicciones.keys()))
            prediccion_info = self.predicciones[prediccion_key]
            
            resultado = {
                'partido': i + 1,
                'local': partido['local'],
                'visitante': partido['visitante'],
                'fecha': partido.get('fecha', 'Sin fecha'),
                'prediccion': prediccion_key,
                'codigo': prediccion_info['codigo'],
                'simbolo': prediccion_info['simbolo']
            }
            
            quiniela.append(resultado)
        
        return quiniela
    
    def generar_quiniela_con_tendencia(self, partidos: List[Dict], tendencia: str = 'equilibrada') -> List[Dict]:
        """
        Genera una quiniela con cierta tendencia en las predicciones
        
        Args:
            partidos: Lista de partidos
            tendencia: 'local', 'visitante', 'empate', o 'equilibrada'
            
        Returns:
            Lista de predicciones con la tendencia especificada
        """
        if tendencia == 'equilibrada':
            return self._generar_quiniela_individual(partidos)
        
        quiniela = []
        
        # Definir probabilidades según la tendencia
        probabilidades = {
            'local': {'Local': 0.5, 'Empate': 0.25, 'Visitante': 0.25},
            'visitante': {'Local': 0.25, 'Empate': 0.25, 'Visitante': 0.5},
            'empate': {'Local': 0.3, 'Empate': 0.4, 'Visitante': 0.3}
        }
        
        prob = probabilidades.get(tendencia, probabilidades['local'])
        
        for i, partido in enumerate(partidos[:14]):
            # Generar predicción con probabilidad sesgada
            rand_val = random.random()
            
            if rand_val < prob['Local']:
                prediccion_key = 'Local'
            elif rand_val < prob['Local'] + prob['Empate']:
                prediccion_key = 'Empate'
            else:
                prediccion_key = 'Visitante'
            
            prediccion_info = self.predicciones[prediccion_key]
            
            resultado = {
                'partido': i + 1,
                'local': partido['local'],
                'visitante': partido['visitante'],
                'fecha': partido.get('fecha', 'Sin fecha'),
                'prediccion': prediccion_key,
                'codigo': prediccion_info['codigo'],
                'simbolo': prediccion_info['simbolo']
            }
            
            quiniela.append(resultado)
        
        return quiniela  # Retornar la quiniela directamente
    
    def calcular_estadisticas_quiniela(self, quiniela: List[Dict]) -> Dict:
        """
        Calcula estadísticas de una quiniela
        
        Args:
            quiniela: Lista de predicciones
            
        Returns:
            Diccionario con estadísticas
        """
        total_partidos = len(quiniela)
        predicciones_count = {}
        
        for resultado in quiniela:
            pred = resultado['prediccion']
            predicciones_count[pred] = predicciones_count.get(pred, 0) + 1
        
        estadisticas = {
            'total_partidos': total_partidos,
            'predicciones': predicciones_count,
            'porcentajes': {
                pred: (count / total_partidos) * 100 
                for pred, count in predicciones_count.items()
            }
        }
        
        return estadisticas
