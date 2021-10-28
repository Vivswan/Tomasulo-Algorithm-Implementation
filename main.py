from src.tomasulo import Tomasulo

if __name__ == '__main__':
    code = """
        # LD R1 0(R2) 
        # SD R1 10(R2) 
        # 
        # BEQ R1, R2, Loop
        # BNE R1, R2, Loop

        ADD R1, R2, R3 
        SUB R1, R1, R3 
        ADDI R1, R2, 5
        # ADDD F1, F2, F3 
        # SUB.D F1, F2, F3 
        SUBi R1, R2, 5
    """
    tomasulo = Tomasulo(code)

    while tomasulo._cycle < 10:
        tomasulo.step()
    print()
    for k in tomasulo.instruction_buffer.full_code:
        print(k)
