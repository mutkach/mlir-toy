int double2(int a)
{
    int b = 42;
    return a + b;
}

int main(int argc, char** argv)
{
    int a = 40;
    int c = double2(a);
    return a;
}
