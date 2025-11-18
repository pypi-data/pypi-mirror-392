import unittest
import sys
import os
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from frame import Frame, fVar, fGet, fExec, fOp, FramerError, FastGet

class TestFrameCore(unittest.TestCase):
    
    def test_basic_frame_creation(self):
        """Тест создания базового фрейма"""
    
    def test_fvar_operations(self):
        """Тест операций с переменными"""
        with Frame() as f:
            # Создание переменных
            fVar('x', 10, framer=f())
            fVar('y', 20, framer=f())
            
            # Получение значений
            self.assertEqual(fGet('x', f()), 10)
            self.assertEqual(fGet('y', f()), 20)
    
    def test_arithmetic_operations(self):
        """Тест арифметических операций"""
        with Frame(safemode=False) as f:
            fVar('a', 15, framer=f())
            fVar('b', 25, framer=f())
            fVar('result', 'a + b', with_eval=True, framer=f())
            
            result = FastGet(f, 'result')
            self.assertEqual(result, 40)
    
    def test_condition_blocks(self):
        """Тест условных блоков"""
        with Frame(safemode=False) as f:
            fVar('x', 10, framer=f())
            fVar('y', 20, framer=f())
            
            fOp.match('x > y', 'result = "x bigger"', 'result = "y bigger"', framer=f())
            fVar('result', 'result', with_eval=True, framer=f())
            
            self.assertEqual(FastGet(f, 'result'), "y bigger")
    
    def test_frame_serialization(self):
        """Тест сериализации фрейма"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            filename = temp_file.name
        
        try:
            # Сохраняем фрейм
            with Frame(safemode=False) as frame:
                frame.Var('test_data', 42)
                frame.save(filename, format='json')
            
            # Загружаем фрейм
            with Frame().load(filename, format='json') as loaded_frame:
                self.assertEqual(loaded_frame.Get('test_data'), 42)
                
        finally:
            os.unlink(filename)
    
    def test_error_handling(self):
        """Тест обработки ошибок"""
        with self.assertRaises(Exception):  # Должна быть конкретная ошибка из твоего фреймворка
            with Frame(safemode=False) as f:
                # Попытка использовать несуществующую переменную
                fVar('invalid', 'undefined_var', with_eval=True, framer=f())
                fExec(f())

if __name__ == '__main__':
    unittest.main()