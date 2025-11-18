import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from frame import Frame, FastGet
from frame import MathPlugin

class TestMathPlugin(unittest.TestCase):
    
    def test_plugin_initialization(self):
        """Тест инициализации плагина"""
        frame = Frame(safemode=False)
        plugin = MathPlugin(frame)
        
        self.assertEqual(plugin.work(), 'mathplugin <v0.1.1>')
        self.assertFalse(plugin._state['included'])
    
    def test_plugin_inclusion(self):
        """Тест включения плагина"""
        frame = Frame(safemode=False)
        plugin = MathPlugin(frame)
        plugin.include()
        
        self.assertTrue(plugin._state['included'])
        # Проверяем, что зависимости добавлены в код
        code = frame.compile()
        self.assertIn('import math, cmath', code)
    
    def test_math_operations(self):
        """Тест математических операций"""
        frame = Frame(safemode=False)
        plugin = MathPlugin(frame).include()
        
        # Тест параболы
        plugin.parabola(5, 'result')
        frame.Exec()
        self.assertEqual(FastGet(frame, 'result'), 25)
        
        # Тест квадратного корня
        plugin.sqrt(16, 'sqrt_result')
        frame.Exec()
        self.assertEqual(FastGet(frame, 'sqrt_result'), 4.0)
    
    def test_complex_math(self):
        """Тест сложных математических функций"""
        frame = Frame(safemode=False)
        plugin = MathPlugin(frame).include()
        
        # Тест дискриминанта
        plugin.discriminant(1, -3, 2, 'disc_result')
        frame.Exec()
        result = FastGet(frame, 'disc_result')
        self.assertEqual(result[2], 1)  # Дискриминант должен быть 1
    
    def test_sigmoid_function(self):
        """Тест функции сигмоиды"""
        frame = Frame(safemode=False)
        plugin = MathPlugin(frame).include()
        
        plugin.sigmoid(0, 'sigmoid_result')
        frame.Exec()
        result = FastGet(frame, 'sigmoid_result')
        self.assertAlmostEqual(result, 0.5, places=5)

if __name__ == '__main__':
    unittest.main()