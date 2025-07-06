#include <stdio.h>
#include <stdlib.h>

// Simple calculator functions
int add(int a, int b) {
    return a + b;
}

int subtract(int a, int b) {
    return a - b;
}

int multiply(int a, int b) {
    return a * b;
}

float divide(int a, int b) {
    if (b == 0) {
        printf("Error: Cannot divide by zero\n");
        return 0;
    }
    return (float)a / b;
}

// Main function
int main() {
    int num1, num2;
    char operation;
    
    printf("Simple Calculator\n");
    printf("Enter first number: ");
    scanf("%d", &num1);
    
    printf("Enter operation (+, -, *, /): ");
    scanf(" %c", &operation);
    
    printf("Enter second number: ");
    scanf("%d", &num2);
    
    switch(operation) {
        case '+':
            printf("Result: %d\n", add(num1, num2));
            break;
        case '-':
            printf("Result: %d\n", subtract(num1, num2));
            break;
        case '*':
            printf("Result: %d\n", multiply(num1, num2));
            break;
        case '/':
            printf("Result: %.2f\n", divide(num1, num2));
            break;
        default:
            printf("Invalid operation\n");
    }
    
    return 0;
} 