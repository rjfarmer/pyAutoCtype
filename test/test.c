#include <stdio.h>
#include <stdlib.h>

typedef struct{
    int a;
    float b;
    int *aptr;
    float *bptr;
    float **bptrptr;
} test_struct;


int intFunc(int i){
    return 2*i;
}

int intFunc2(int i, int j){
    return i+j;
}

float floatFunc(float i){
    return 2.0*i;
}

float floatFunc2(float i, float j){
    return i+j;
}
