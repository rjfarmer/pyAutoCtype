#include <stdio.h>
#include <stdlib.h>

typedef struct{
    int a;
    float b;
    int *aptr;
    float *bptr;
    float **bptrptr;
} test_struct;

typedef struct{
    int a2;
    test_struct b1;
} test_struct2;


// typedef struct test_struct3 test_struct3;

// struct test_struct3{
//     int a3;
//     test_struct3 *b1;
// };

typedef struct test_struct3 {
    int a3;
    struct test_struct3 *b1;
} test_struct3;

test_struct3 ts3_1;
test_struct ts1_arr1[5];

union Data{
    int a;
    float b;
} test_union;

int g_a_int = 1;
float b_float = 5;
float g_b_float;
float *p_b_float, **p2_b_float;
int int_arr[10],int_arr2[10][5];
test_struct2 ts2_1;

const int const_int=5;
const float pi=3.14;

#define MYDEF 1;


void setpPtr(){
    p_b_float = &b_float;
    p2_b_float = &p_b_float;
}

int intFuncNoArgs(){
    return 42;
}

int intFunc1(int i1){
    return 2*i1;
}

int intFunc2(int i2, int j2){
    return i2+j2;
}

int floatFuncNoArgs(){
    return 99.0;
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

float floatptrFunc1(float * i5){
    return *i5;
}

float structFunc2(test_struct * i5){
    return (*i5).b + 5.0;
}