import unittest
import sys
import os
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from frame import FramesComposer, Frame, fVar, FastGet

class TestFramesComposer(unittest.TestCase):
    
    def test_composer_creation(self):
        """Тест создания композитора"""
        with FramesComposer() as fc:
            self.assertIsNotNone(fc.superglobal())
            self.assertEqual(fc._arch, 'dict')
    
    def test_frame_loading(self):
        """Тест загрузки фреймов в композитор"""
        with FramesComposer() as fc:
            frame1 = Frame(name='test1')
            frame2 = Frame(name='test2')
            
            fc.load_frame('processor', frame1)
            fc.load_frame('validator', frame2)
            
            self.assertIn('processor', fc._frames)
            self.assertIn('validator', fc._frames)
    
    def test_frame_synchronization(self):
        """Тест синхронизации фреймов"""
        with FramesComposer(safemode=False) as fc:
            fc['frame1'] = Frame(safemode=False)
            fc['frame2'] = Frame(safemode=False)
            
            fc['frame1'].Var('shared_data', 100)
            fc.sync('frame1', 'frame2')
            
            # После синхронизации frame2 должен видеть переменную
            self.assertEqual(fc['frame2'].Get('shared_data'), 100)
    
    def test_composer_serialization(self):
        """Тест сериализации композитора"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            filename = temp_file.name
        
        try:
            # Создаем и сохраняем композицию
            with FramesComposer(safemode=False) as fc:
                fc['main'] = Frame(safemode=False)
                fc['main'].Var('app_state', 'running')
                fc.save(filename, format='json')
            
            # Загружаем композицию
            loaded_fc = FramesComposer.from_file(filename, format='json')
            self.assertEqual(loaded_fc['main'].Get('app_state'), 'running')
            
        finally:
            os.unlink(filename)
    
    def test_composer_execution(self):
        """Тест выполнения композитора"""
        with FramesComposer(safemode=False) as fc:
            fc['math_frame'] = Frame(safemode=False)
            fc['math_frame'].Var('x', 10)
            fc['math_frame'].Var('y', 5)
            fc['math_frame'].Var('result', 'x * y', with_eval=True)
            
            # Выполняем всю композицию
            fc.test_exec()
            
            # Проверяем результат
            self.assertEqual(FastGet(fc['math_frame'], 'result'), 50)

if __name__ == '__main__':
    unittest.main()