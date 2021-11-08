def extract_rbits(number, bits):
    b_num = bin(number).split('b')[1][-bits:]
    num_int = int(b_num, 2)
    return num_int
