int result = 0;

func printD() {
    print();
    print("1. Сложение (a + b)");
    print("2. Вычитание (a - b)");
    print("3. Умножение (a * b)");
    print("4. Деление (a / b)");
    print("5. Степень (a ** b)");
    print("6. Цел. деление (a // b)");
    print("7. Остаток от деления (a % b)");
    print();
}

func main() {
    print("Калькулятор");
    int n1 = input("Введи первое число (a):");
    int n2 = input("Введи второе число (b):");
    printD();
    int t = input("Выберите действие:");

    try {
        if t == 1 {result = n1 + n2;}
        else if t == 2 {result = n1 - n2;}
        else if t == 3 {result = n1 * n2;}
        else if t == 4 {result = n1 / n2;}
        else if t == 5 {result = n1 ** n2;}
        else if t == 6 {result = n1 // n2;}
        else if t == 7 {result = n1 % n2;}
    }
    except as e {
        print("Произошла ошибка: " + e);
    }

    print();
    print("Ответ: " + result);

    return 0;
}