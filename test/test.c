#include <stdio.h>
#include <stdlib.h>

typedef struct{
    int a;
    float b;
    int *aptr;
    float *bptr;
    float **bptrptr;
} test_struct;

int g_a_int = 1;
float g_b_float;

#define MYDEF 1;


int intFunc1(int i1){
    return 2*i1;
}

int intFunc2(int i2, int j2){
    return i2+j2 + g_a_int + MYDEF;
}

float floatFunc1(float i3){
    return 2.0*i3;
}

float floatFunc2(float i4, float j4){
    return i4+j4;
}

float structFunc1(test_struct i5){
    return i5.b + 5.0;
}
