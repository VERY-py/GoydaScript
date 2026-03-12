# Функция для вычисления факториала
func factorial(n) {
    if n <= 1 {
        return 1;
    }
    return n * factorial(n - 1);
}

# Функция для вычисления чисел Фибоначчи
func fibonacci(n) {
    if n <= 1 {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

# Функция с несколькими параметрами
func power(base, exp) {
    int result = 1;
    int i = 0;
    while i < exp {
        result = result * base;
        i += 1;
    }
    return result;
}

func main() {
    # Вызов функций
    int fact5 = factorial(5);
    print("Факториал 5 = " + fact5);

    int fib7 = fibonacci(7);
    print("Число Фибоначчи(7) = " + fib7);

    int pow2_10 = power(2, 10);
    print("2 в степени 10 = " + pow2_10);

    # Демонстрация while
    int counter = 5;
    print("Обратный отсчет:");
    while counter > 0 {
        print(counter);
        counter -= 1;
    }
    print("Старт!");

    return 0;
}