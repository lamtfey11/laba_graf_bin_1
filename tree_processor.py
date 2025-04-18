from typing import List, Optional
import graphviz
import os
import subprocess
import sys
import random
import time

# Настройка Graphviz (убедитесь, что путь правильный)
graphviz_path = r'C:\Users\elena\Downloads\Graphviz-12.2.1-win64\bin'
os.environ["PATH"] = graphviz_path + os.pathsep + os.environ["PATH"]

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class TreeBuilder:
    def build_tree(self, values: List[Optional[int]]) -> Optional[TreeNode]:
        """Построение дерева из списка значений (уровневой порядок)"""
        if not values or values[0] is None:
            return None

        root = TreeNode(values[0])
        queue = [root]
        i = 1

        while queue and i < len(values):
            node = queue.pop(0)

            if i < len(values) and values[i] is not None:
                node.left = TreeNode(values[i])
                queue.append(node.left)
            i += 1

            if i < len(values) and values[i] is not None:
                node.right = TreeNode(values[i])
                queue.append(node.right)
            i += 1

        return root

    def serialize_structure(self, root: Optional[TreeNode]) -> str:
        """Сериализация структуры дерева"""
        if not root:
            return 'N'
        return f"({self.serialize_structure(root.left)},{self.serialize_structure(root.right)})"

    def find_subtrees(self, main_root: TreeNode, target_struct: str) -> List[TreeNode]:
        """Поиск всех поддеревьев с заданной структурой"""
        result = []

        def dfs(node: Optional[TreeNode]) -> str:
            if not node:
                return 'N'
            current = f"({dfs(node.left)},{dfs(node.right)})"
            if current == target_struct:
                result.append(node)
            return current

        dfs(main_root)
        return result

class TreeVisualizer:
    def draw_tree(self, root: Optional[TreeNode], filename: str, highlight: bool = False):
        """Генерация изображения дерева с помощью Graphviz"""
        dot = graphviz.Digraph(format='png', graph_attr={'ordering': 'out'})

        def add_nodes(node, parent=None):
            if node:
                node_id = str(id(node))
                color = 'red' if highlight and node == root else 'black'
                dot.node(node_id, str(node.val), color=color)
                if parent:
                    dot.edge(parent, node_id)
                add_nodes(node.left, node_id)
                add_nodes(node.right, node_id)

        add_nodes(root)
        dot.render(filename, cleanup=True)

class FileProcessor:
    def __init__(self):
        self.builder = TreeBuilder()
        self.visualizer = TreeVisualizer()

    def generate_random_tree(self, size: int) -> List[Optional[int]]:
        """Генерация случайного дерева заданного размера"""
        if size == 0:
            return []
        
        values = [random.randint(1, 100)]  # Корень всегда существует
        for _ in range(size - 1):
            # Вероятность None регулирует "густоту" дерева
            values.append(random.randint(1, 100) if random.random() > 0.3 else None)
        return values

    def process_tree(self, size: int, target_size: int = None):
        """Обработка дерева заданного размера"""
        if target_size is None:
            target_size = max(2, size // 10)  # Размер поддерева ~10% от основного

        # Генерация деревьев
        main_values = self.generate_random_tree(size)
        target_values = self.generate_random_tree(target_size)

        # Построение деревьев
        main_root = self.builder.build_tree(main_values)
        target_root = self.builder.build_tree(target_values)

        # Измерение времени работы алгоритма
        start_time = time.perf_counter_ns()
        target_struct = self.builder.serialize_structure(target_root)
        matches = self.builder.find_subtrees(main_root, target_struct)
        end_time = time.perf_counter_ns()
        elapsed_time = (end_time - start_time) / 1000  # мкс

        # Генерация изображений (только для небольших деревьев)
        if size <= 1000:  # Ограничение на визуализацию
            self.visualizer.draw_tree(main_root, f"tree_{size}", highlight=bool(matches))
            for i, node in enumerate(matches, 1):
                self.visualizer.draw_tree(node, f"subtree_{size}_{i}", highlight=True)

        print(f"Обработка дерева с {size} узлами")
        print(f"Время работы алгоритма: {elapsed_time:.0f} мкс")
        print(f"Сгенерировано файлов: {len(matches) + 1 if size <= 1000 else 0}\n")

if __name__ == "__main__":
    random.seed(42)  # Для воспроизводимости результатов
    processor = FileProcessor()

    # Обработка деревьев разного размера
    for size in [10, 100, 1000, 10000, 100000]:
        processor.process_tree(size)