class AVLNode:
    def __init__(self, data_ptr):
        self.data_ptr = data_ptr
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    def __init__(self, key_func):
        """
        key_func: Một hàm (lambda) để trích xuất khóa chính từ data_ptr (ví dụ: book_id hoặc reader_id)
        """
        self.root = None
        self.key_func = key_func

    def _get_key(self, data_ptr):
        if data_ptr is None:
            return None
        return self.key_func(data_ptr)

    def _height(self, node):
        if not node:
            return 0
        return node.height

    def _get_balance(self, node):
        if not node:
            return 0
        return self._height(node.left) - self._height(node.right)

    def _right_rotate(self, y):
        x = y.left
        T2 = x.right

        # Perform rotation
        x.right = y
        y.left = T2

        # Update heights
        y.height = max(self._height(y.left), self._height(y.right)) + 1
        x.height = max(self._height(x.left), self._height(x.right)) + 1

        return x

    def _left_rotate(self, x):
        y = x.right
        T2 = y.left

        # Perform rotation
        y.left = x
        x.right = T2

        # Update heights
        x.height = max(self._height(x.left), self._height(x.right)) + 1
        y.height = max(self._height(y.left), self._height(y.right)) + 1

        return y

    def insert(self, data):
        self.root = self._insert_node(self.root, data)

    def _insert_node(self, node, data):
        if not node:
            return AVLNode(data)

        key = self._get_key(data)
        node_key = self._get_key(node.data_ptr)

        if key < node_key:
            node.left = self._insert_node(node.left, data)
        elif key > node_key:
            node.right = self._insert_node(node.right, data)
        else:
            return node # Duplicate keys are not allowed

        # Update height
        node.height = 1 + max(self._height(node.left), self._height(node.right))

        # Get balance factor
        balance = self._get_balance(node)

        # Balance the tree
        # Left Left
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._right_rotate(node)

        # Left Right
        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        # Right Right
        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._left_rotate(node)

        # Right Left
        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def search(self, key):
        return self._search_node(self.root, key)

    def _search_node(self, node, key):
        if node is None:
            return None
        
        node_key = self._get_key(node.data_ptr)
        
        if key == node_key:
            return node.data_ptr
        elif key < node_key:
            return self._search_node(node.left, key)
        else:
            return self._search_node(node.right, key)

    def _min_value_node(self, node):
        if node is None or node.left is None:
            return node
        return self._min_value_node(node.left)

    def delete(self, key):
        self.root = self._delete_node(self.root, key)

    def _delete_node(self, node, key):
        if not node:
            return node

        node_key = self._get_key(node.data_ptr)

        if key < node_key:
            node.left = self._delete_node(node.left, key)
        elif key > node_key:
            node.right = self._delete_node(node.right, key)
        else:
            # Node to delete found
            if node.left is None:
                temp = node.right
                node = None
                return temp
            elif node.right is None:
                temp = node.left
                node = None
                return temp
            
            # Node with two children
            temp = self._min_value_node(node.right)
            node.data_ptr = temp.data_ptr
            node.right = self._delete_node(node.right, self._get_key(temp.data_ptr))

        if node is None:
            return node

        # Update height
        node.height = 1 + max(self._height(node.left), self._height(node.right))

        # Rebalance
        balance = self._get_balance(node)

        # Left Left
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._right_rotate(node)

        # Left Right
        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        # Right Right
        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._left_rotate(node)

        # Right Left
        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def in_order(self):
        """Returns a list of all elements in sorted order by key."""
        result = []
        self._in_order_node(self.root, result)
        return result

    def _in_order_node(self, node, result):
        if node:
            self._in_order_node(node.left, result)
            result.append(node.data_ptr)
            self._in_order_node(node.right, result)
