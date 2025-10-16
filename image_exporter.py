from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict
import io
from datetime import datetime

class QuinielaImageExporter:
    """Clase para exportar quinielas como imágenes"""
    
    def __init__(self):
        self.width = 800
        self.header_height = 120
        self.row_height = 50
        self.footer_height = 80
        
        # Colores característicos de Progol
        self.color_verde = (46, 139, 87)  # Verde Progol
        self.color_blanco = (255, 255, 255)
        self.color_gris_claro = (240, 248, 255)
        self.color_gris = (128, 128, 128)
        self.color_negro = (0, 0, 0)
    
    def generar_imagen(self, quiniela: List[Dict], numero_quiniela: int = 1) -> bytes:
        """
        Genera una imagen PNG de la quiniela
        
        Args:
            quiniela: Lista de predicciones
            numero_quiniela: Número de quiniela para el título
            
        Returns:
            Bytes de la imagen PNG
        """
        num_partidos = len(quiniela)
        total_height = self.header_height + (num_partidos * self.row_height) + self.footer_height
        
        # Crear imagen
        img = Image.new('RGB', (self.width, total_height), self.color_blanco)
        draw = ImageDraw.Draw(img)
        
        # Dibujar header
        self._draw_header(draw, numero_quiniela)
        
        # Dibujar partidos
        y_offset = self.header_height
        for i, partido in enumerate(quiniela):
            self._draw_partido(draw, partido, y_offset, i % 2 == 0)
            y_offset += self.row_height
        
        # Dibujar footer
        self._draw_footer(draw, quiniela, y_offset)
        
        # Convertir a bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes.getvalue()
    
    def _draw_header(self, draw: ImageDraw, numero_quiniela: int):
        """Dibuja el encabezado de la quiniela"""
        # Fondo verde
        draw.rectangle([0, 0, self.width, self.header_height], fill=self.color_verde)
        
        # Título
        try:
            font_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        except:
            font_titulo = ImageFont.load_default()
        
        titulo = f"QUINIELA PROGOL #{numero_quiniela}"
        bbox = draw.textbbox((0, 0), titulo, font=font_titulo)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        draw.text((x, 20), titulo, fill=self.color_blanco, font=font_titulo)
        
        # Fecha
        try:
            font_fecha = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            font_fecha = ImageFont.load_default()
        
        fecha_texto = datetime.now().strftime("%d/%m/%Y %H:%M")
        bbox = draw.textbbox((0, 0), fecha_texto, font=font_fecha)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        draw.text((x, 75), fecha_texto, fill=self.color_blanco, font=font_fecha)
    
    def _draw_partido(self, draw: ImageDraw, partido: Dict, y_offset: int, fondo_claro: bool):
        """Dibuja una fila de partido"""
        # Fondo alternado
        if fondo_claro:
            draw.rectangle([0, y_offset, self.width, y_offset + self.row_height], 
                         fill=self.color_gris_claro)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        except:
            font = ImageFont.load_default()
            font_bold = ImageFont.load_default()
        
        # Número de partido
        num_partido = str(partido['partido'])
        draw.text((20, y_offset + 15), num_partido, fill=self.color_gris, font=font_bold)
        
        # Equipos
        local = partido['local'][:25]  # Limitar longitud
        visitante = partido['visitante'][:25]
        
        equipos_texto = f"{local} vs {visitante}"
        draw.text((60, y_offset + 15), equipos_texto, fill=self.color_negro, font=font)
        
        # Predicción
        prediccion_texto = f"{partido['simbolo']} {partido['prediccion']}"
        bbox = draw.textbbox((0, 0), prediccion_texto, font=font_bold)
        text_width = bbox[2] - bbox[0]
        x = self.width - text_width - 30
        
        # Fondo para la predicción
        draw.rectangle([x - 10, y_offset + 10, x + text_width + 10, y_offset + 40],
                      fill=self.color_verde, outline=self.color_verde)
        draw.text((x, y_offset + 15), prediccion_texto, fill=self.color_blanco, font=font_bold)
    
    def _draw_footer(self, draw: ImageDraw, quiniela: List[Dict], y_offset: int):
        """Dibuja el pie de página con resumen"""
        # Línea separadora
        draw.line([20, y_offset, self.width - 20, y_offset], 
                 fill=self.color_gris, width=2)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        # Calcular resumen
        predicciones = {}
        for p in quiniela:
            pred = p['prediccion']
            predicciones[pred] = predicciones.get(pred, 0) + 1
        
        # Mostrar resumen
        resumen = f"Locales: {predicciones.get('Local', 0)} | Empates: {predicciones.get('Empate', 0)} | Visitantes: {predicciones.get('Visitante', 0)}"
        bbox = draw.textbbox((0, 0), resumen, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        draw.text((x, y_offset + 20), resumen, fill=self.color_gris, font=font)
        
        # Disclaimer
        disclaimer = "Predicciones aleatorias - Solo para entretenimiento"
        bbox = draw.textbbox((0, 0), disclaimer, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        draw.text((x, y_offset + 45), disclaimer, fill=self.color_gris, font=font)
