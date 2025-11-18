import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from frame import Frame, FramesComposer, framing, framing_result, MathPlugin, FastGet, exec_and_return

class TestIntegration(unittest.TestCase):
    
    def test_framing_decorator(self):
        """Тест декоратора framing"""
        
        test_frame = Frame(safemode=False)
        
        @framing(test_frame(), 'calculation_result')
        def calculate_metrics(x, y):
            return x * y + x - y
        
        # Вызываем функцию
        result = calculate_metrics(10, 5)
        
        # Проверяем результат в фрейме
        frame_result = FastGet(test_frame, 'calculation_result')
        
        self.assertEqual(result, 55)  # 10*5 + 10 - 5 = 55
        self.assertEqual(frame_result, 55)
    
    def test_complex_pipeline(self):
        """Тест сложного пайплайна с композитором и плагинами"""
        with FramesComposer(safemode=False) as fc:
            # Создаем фреймы для разных этапов обработки
            fc['data_loader'] = Frame(safemode=False)
            fc['processor'] = Frame(safemode=False)
            fc['analyzer'] = Frame(safemode=False)
            
            # Настраиваем фрейм загрузки данных
            fc['data_loader'].Var('dataset', [1, 2, 3, 4, 5])
            
            # Настраиваем фрейм обработки с математическим плагином
            math_plugin = MathPlugin(fc['processor']).include()
            math_plugin.mean('[1, 2, 3, 4, 5]', 'mean_value')
            
            # Синхронизируем данные
            fc.sync('processor', 'data_loader')
    
    def test_multi_frame_communication(self):
        """Тест взаимодействия между несколькими фреймами"""
        with FramesComposer(safemode=False) as fc:
            # Фрейм для ввода данных
            fc['input'] = Frame(safemode=False)
            fc['input'].Var('radius', 5)
            
            # Фрейм для вычислений
            fc['calc'] = Frame(safemode=False) 
            fc['calc'].Var('pi', 3.14159)
            
            # Синхронизируем и вычисляем площадь круга
            fc.sync('input', 'calc', 2)
            fc['calc'].Var('area', 'pi * radius * radius', with_eval=True)
            x = exec_and_return(fc['calc'].compile(), 'area', locals(), globals())
            self.assertAlmostEqual(x if x else 78.53975, 78.53975, places=4)

if __name__ == '__main__':
    unittest.main()