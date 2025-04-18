from typing import List, Optional  # Это критически важно!
import graphviz
import os
import subprocess
import sys

# Укажите правильный путь к Graphviz
graphviz_path = r'C:\Users\elena\Downloads\Graphviz-12.2.1-win64\bin'
os.environ["PATH"] = graphviz_path + os.pathsep + os.environ["PATH"]

# Проверка доступности Graphviz
try:
    result = subprocess.run(
        [os.path.join(graphviz_path, 'dot.exe'), '-V'],
        capture_output=True,
        text=True,
        check=True
    )
    print("Graphviz работает:", result.stdout.split('\n')[0])
except Exception as e:
    print("Ошибка Graphviz:", str(e))
    sys.exit(1)

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

            if values[i] is not None:
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

    def process_file(self, input_file: str):
        """Обработка входного файла и генерация результатов"""
        try:
            with open(input_file, 'r') as f:
                lines = f.read().splitlines()

            if len(lines) < 2:
                raise ValueError("Файл должен содержать две строки: основное дерево и целевое поддерево")

            # Преобразование входных данных
            main_values = [int(x) if x != 'None' else None for x in lines[0].split()]
            target_values = [int(x) if x != 'None' else None for x in lines[1].split()]

            # Построение деревьев
            main_root = self.builder.build_tree(main_values)
            target_root = self.builder.build_tree(target_values)

            if not target_root:
                raise ValueError("Целевое поддерево не может быть пустым")

            # Поиск совпадений
            target_struct = self.builder.serialize_structure(target_root)
            matches = self.builder.find_subtrees(main_root, target_struct)

            # Генерация изображений
            self.visualizer.draw_tree(main_root, "main_tree", highlight=bool(matches))
            for i, node in enumerate(matches, 1):
                self.visualizer.draw_tree(node, f"subtree_{i}", highlight=True)

            print(f"Сгенерировано файлов: {len(matches) + 1}")

        except Exception as e:
            print(f"Ошибка: {str(e)}")
            exit(1)


if __name__ == "__main__":
    processor = FileProcessor()
    processor.process_file("input.txt")
