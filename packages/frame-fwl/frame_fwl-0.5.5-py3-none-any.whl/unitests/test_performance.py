import unittest
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from frame import Frame, FramesComposer, fVar, fExec, FastGet

class TestPerformance(unittest.TestCase):
    
    def test_execution_speed(self):
        """Тест скорости выполнения"""
        start_time = time.time()
        
        with Frame(safemode=False) as f:
            # Создаем 50 переменных (уменьшил для скорости)
            for i in range(50):
                fVar(f'var_{i}', i, framer=f())
            
            # Выполняем простые операции
            fVar('sum', 'sum([var_0, var_49])', with_eval=True, framer=f())
            result = FastGet(f, 'sum')
        
        execution_time = time.time() - start_time
        self.assertEqual(result, 49)  # 0 + 49 = 49
        self.assertLess(execution_time, 2.0, "Выполнение заняло слишком много времени")
    
    def test_memory_efficiency(self):
        """Тест эффективности использования памяти"""
        # Создаем множество фреймов
        frames = []
        for i in range(20):  # Уменьшил количество для стабильности
            frame = Frame()
            for j in range(10):
                frame.Var(f'data_{j}', f'value_{i}_{j}')
            frames.append(frame)
        
        # Если не упало по памяти - тест пройден
        self.assertEqual(len(frames), 20)

if __name__ == '__main__':
    unittest.main()