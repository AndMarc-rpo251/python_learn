numbers = list(range(1, 11))
even_numbers = [n for n in numbers if n % 2 == 0]
print("1) Чётные:", even_numbers)

products = {
    "яблоко": 100,
    "банан": 80,
    "молоко": 120,
}
products["хлеб"] = 70
products["яблоко"] = 110

print("2) Товары и цены:")
for product, price in products.items():
    print(f"   {product}: {price}")

tags = ["python", "flask", "python", "oop", "flask", "list"]
unique_tags = set(tags)
print("3) Уникальные теги:", unique_tags)
print("   'python' in tags:", "python" in unique_tags)

point = (10, 20)
try:
    point[0] = 100
except TypeError as error:
    print("4) TypeError пойман:", error)


squares_loop = []
for n in numbers:
    squares_loop.append(n ** 2)

squares_comprehension = [n ** 2 for n in numbers]

print("5) Квадраты через for:", squares_loop)
print("   Квадраты через comprehension:", squares_comprehension)

# Проверка из задания
assert isinstance(numbers, list)
assert isinstance(products, dict)
assert isinstance(unique_tags, set)
assert isinstance(point, tuple)

assert squares_loop == squares_comprehension
print("OK")
