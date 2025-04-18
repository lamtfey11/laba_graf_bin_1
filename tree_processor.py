from typing import List, Optional
import graphviz
import os
import subprocess
import sys
import random
import time
import glob

# Настройка Graphviz
graphviz_path = r'C:\Users\elena\Downloads\Graphviz-12.2.1-win64\bin'
os.environ["PATH"] = graphviz_path + os.pathsep + os.environ["PATH"]

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class TreeBuilder:
    def build_tree(self, values: List[Optional[int]]) -> Optional[TreeNode]:
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
        if not root:
            return 'N'
        return f"({self.serialize_structure(root.left)},{self.serialize_structure(root.right)})"

    def find_subtrees(self, main_root: TreeNode, target_struct: str) -> List[TreeNode]:
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
    def __init__(self):
        self.cleanup_old_images()

    def cleanup_old_images(self):
        for file in glob.glob("tree_*.png") + glob.glob("subtree_*.png") + glob.glob("main_tree.png"):
            try:
                os.remove(file)
            except OSError:
                pass

    def draw_simplified_tree(self, root: Optional[TreeNode], filename: str, max_nodes: int = 50):
        dot = graphviz.Digraph(format='png', graph_attr={'ordering': 'out'})
        nodes_added = 0

        def add_nodes(node, parent=None):
            nonlocal nodes_added
            if node and nodes_added < max_nodes:
                node_id = str(id(node))
                dot.node(node_id, str(node.val))
                if parent:
                    dot.edge(parent, node_id)
                nodes_added += 1
                if nodes_added < max_nodes:
                    add_nodes(node.left, node_id)
                    add_nodes(node.right, node_id)
                else:
                    dot.node(f"skip_{node_id}", f"... {self.count_nodes(node) - 1} nodes skipped", shape='plaintext')
                    dot.edge(node_id, f"skip_{node_id}", style='dashed')

        add_nodes(root)
        dot.render(filename, cleanup=True)

    def count_nodes(self, root: Optional[TreeNode]) -> int:
        if not root:
            return 0
        return 1 + self.count_nodes(root.left) + self.count_nodes(root.right)

    def draw_tree(self, root: Optional[TreeNode], filename: str, highlight: bool = False, max_full_size: int = 500):
        if self.count_nodes(root) > max_full_size:
            self.draw_simplified_tree(root, filename)
        else:
            self.draw_full_tree(root, filename, highlight)

    def draw_full_tree(self, root: Optional[TreeNode], filename: str, highlight: bool = False):
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
        if size == 0:
            return []
        values = [random.randint(1, 100)]
        for _ in range(size - 1):
            values.append(random.randint(1, 100) if random.random() > 0.3 else None)
        return values

    def process_tree(self, size: int):
        self.visualizer.cleanup_old_images()

        # Генерация основного дерева
        main_values = self.generate_random_tree(size)
        main_root = self.builder.build_tree(main_values)

        # Визуализация
        self.visualizer.draw_tree(main_root, f"tree_{size}", highlight=False)
        print(f"\nОсновное дерево из {size} узлов сгенерировано и сохранено в 'tree_{size}.png'")

        # Повторный ввод поддеревьев
        while True:
            raw_input = input("\nВведите значения поддерева (через пробел, используйте 'None' для пустых узлов), или 'exit' для выхода:\n> ")

            if raw_input.strip().lower() == "exit":
                print("Выход к главному меню.\n")
                break

            try:
                target_values = [int(x) if x != 'None' else None for x in raw_input.strip().split()]
                target_root = self.builder.build_tree(target_values)

                if not target_root:
                    print("Ошибка: введено пустое поддерево.")
                    continue

                # Поиск совпадений
                start_time = time.perf_counter_ns()
                target_struct = self.builder.serialize_structure(target_root)
                matches = self.builder.find_subtrees(main_root, target_struct)
                end_time = time.perf_counter_ns()
                elapsed_time = (end_time - start_time) / 1000  # мкс

                # Визуализация найденных совпадений
                for i, node in enumerate(matches[:5], 1):
                    self.visualizer.draw_tree(node, f"subtree_{size}_{i}", highlight=True)

                print(f"\nРезультаты для дерева из {size} узлов:")
                print(f"- Время работы: {elapsed_time:.0f} мкс")
                print(f"- Найдено поддеревьев: {len(matches)}")
                print(f"- Созданы файлы: tree_{size}.png, subtree_{size}_*.png")

            except Exception as e:
                print(f"Ошибка при обработке поддерева: {str(e)}")

    def process_input_file(self, filename: str = "input.txt"):
        self.visualizer.cleanup_old_images()

        try:
            with open(filename, 'r') as f:
                lines = f.read().splitlines()

            if len(lines) < 2:
                raise ValueError("Файл должен содержать две строки: основное дерево и целевое поддерево")

            main_values = [int(x) if x != 'None' else None for x in lines[0].split()]
            target_values = [int(x) if x != 'None' else None for x in lines[1].split()]

            main_root = self.builder.build_tree(main_values)
            target_root = self.builder.build_tree(target_values)

            if not target_root:
                raise ValueError("Целевое поддерево не может быть пустым")

            start_time = time.perf_counter_ns()
            target_struct = self.builder.serialize_structure(target_root)
            matches = self.builder.find_subtrees(main_root, target_struct)
            end_time = time.perf_counter_ns()
            elapsed_time = (end_time - start_time) / 1000

            self.visualizer.draw_tree(main_root, "main_tree", highlight=bool(matches))
            for i, node in enumerate(matches, 1):
                self.visualizer.draw_tree(node, f"subtree_{i}", highlight=True)

            print("\nРезультаты обработки input.txt:")
            print(f"- Время работы: {elapsed_time:.0f} мкс")
            print(f"- Найдено поддеревьев: {len(matches)}")
            print(f"- Созданы файлы: main_tree.png, subtree_*.png")

        except Exception as e:
            print(f"Ошибка: {str(e)}")

def show_menu():
    print("\n" + "=" * 40)
    print("Меню:")
    print("1. Работа с файлом input.txt")
    print("2. Генерация дерева (10 узлов)")
    print("3. Генерация дерева (100 узлов)")
    print("4. Генерация дерева (1000 узлов)")
    print("5. Генерация дерева (10000 узлов)")
    print("6. Генерация дерева (100000 узлов)")
    print("7. Генерация дерева (1000000 узлов)")
    print("0. Выход")
    print("=" * 40)
    return input("Выберите действие (0-7): ").strip()

if __name__ == "__main__":
    # random.seed(42)  # Если хочешь фиксированное поведение — раскомментируй
    processor = FileProcessor()

    while True:
        choice = show_menu()

        if choice == "1":
            processor.process_input_file()
        elif choice == "2":
            processor.process_tree(10)
        elif choice == "3":
            processor.process_tree(100)
        elif choice == "4":
            processor.process_tree(1000)
        elif choice == "5":
            processor.process_tree(10000)
        elif choice == "6":
            processor.process_tree(100000)
        elif choice == "7":
            processor.process_tree(1000000)
        elif choice == "0":
            print("Выход из программы.")
            break
        else:
            print("Неверный ввод. Попробуйте снова.")
