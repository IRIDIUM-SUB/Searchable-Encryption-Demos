'''
Author: I-Hsien
Date: 2021-02-19 10:18:11
LastEditTime: 2021-02-19 10:38:23
LastEditors: I-Hsien
Description: For gen stream by LSFR+Gaffe, refering https://crushonu.top/python%E5%AE%9E%E7%8E%B0lfsr-geffe%E5%AF%86%E9%92%A5%E6%B5%81%E7%94%9F%E6%88%90%E5%99%A8-2/#%E5%85%B7%E4%BD%93%E5%AE%9E%E7%8E%B0%E4%BB%A3%E7%A0%81
FilePath: \Searchable-Encryption-Demos\SWP Solution\LSFR.py
Comments: None
'''
import re
import Log as log

# 检查输入的二进制数
def check_bin_input(input_str, bin_len):
    while re.search(r"[^01]", input_str):
        input_str = input("输入错误，请输入二进制数：")
    while not len(input_str) == bin_len:
        input_str = input("输入长度错误，请输入长度为{}的二进制数：".format(bin_len))
    return input_str


# （输出一个密钥位后）返回进行移位之后的下一轮初始状态
def get_next_initial_bin(lfsr_initial_bin, feedback_f_c_bin):
    not_first = False  # 标记是否已经得到异或运算的第一个位的值
    gf_current_int = 0  # 初始化
    if not len(lfsr_initial_bin) == len(feedback_f_c_bin):
        print("*Error in get_next_initial_bin: data length not equal")
        exit()
    for index in range(len(feedback_f_c_bin)-1, -1, -1):
        coefficient_c = int(feedback_f_c_bin[index])
        # 因为得到第一个异或运算的值后not_first会变为True
        # 所以使用not_first的这两个if判断的先后顺序有讲究
        if (not_first is True) and (coefficient_c == 1):
            # 当前异或（GF(2)）运算的结果
            gf_current_int = int(gf_current_int) ^ int(lfsr_initial_bin[index])  
        # 首先要得到进行异或运算的第一个位的值
        if (not_first is False) and (coefficient_c == 1):
            # 异或（GF(2)）运算的第一个值
            gf_current_int = int(lfsr_initial_bin[index])  
            not_first = True
    return str(gf_current_int) + lfsr_initial_bin[0:len(lfsr_initial_bin) - 1]


# Geffe序列生成器
def geffe_generator(lfsr1_int, lfsr2_int, lfsr3_int):
    if lfsr2_int == 1:
        return (lfsr1_int & 1) ^ (lfsr3_int & 0)
    elif lfsr2_int == 0:
        return (lfsr1_int & 0) ^ (lfsr3_int & 1)


def main(seed:list,output_len:int,N_LEVEL=5):
    # LFSR反馈函数的常数c
    feedback_f_c_bin_array = [0, 0, 0]
    # 三个LFSR的初始状态，及目前处理的状态
    lfsr_initial_bin_array = ['0', '0', '0']
    current_lfsr_bin_array = ['0', '0', '0']
    # n_level=线性反馈移位寄存器的级数
    n_level = N_LEVEL
    for i in range(3):
        feedback_f_c_bin_array[i] = seed[i]
        feedback_f_c_bin_array[i] = check_bin_input(feedback_f_c_bin_array[i], n_level)
    for i in range(3):
        lfsr_initial_bin_array[i] = seed[i+3]
        current_lfsr_bin_array[i] = lfsr_initial_bin_array[i] = check_bin_input(lfsr_initial_bin_array[i], n_level)

    # 开始移位输出密钥流
    
    output_str = ''  # 储存输出的密钥流
    for i in range(output_len):
        lfsr1_int = int(current_lfsr_bin_array[0][n_level-1])
        lfsr2_int = int(current_lfsr_bin_array[1][n_level-1])
        lfsr3_int = int(current_lfsr_bin_array[2][n_level-1])
        output_str = output_str + str(geffe_generator(lfsr1_int, lfsr2_int, lfsr3_int))
        # 更新寄存器中的初始状态
        for j in range(3):
            current_lfsr_bin_array[j] = get_next_initial_bin(current_lfsr_bin_array[j], feedback_f_c_bin_array[j])
    # 输出结果
    print(type(output_str))
    log.log.debug("LSFR stream is:%s",output_str)
    return output_str
    '''Not used
    # 加密
    plaintext_input = input("\n-----加密-----\n明文：")
    ciphertext_output = ''
    key_output = ''
    # #初始化密钥流生成器
    for i in range(3):
        feedback_f_c_bin_array[i] = feedback_f_c_bin_array[i]
    for i in range(3):
        current_lfsr_bin_array[i] = lfsr_initial_bin_array[i] = lfsr_initial_bin_array[i]
    # #逐位加密
    for i in range(len(plaintext_input)):
        lfsr1_int = int(current_lfsr_bin_array[0][n_level - 1])
        lfsr2_int = int(current_lfsr_bin_array[1][n_level - 1])
        lfsr3_int = int(current_lfsr_bin_array[2][n_level - 1])
        key = int(geffe_generator(lfsr1_int, lfsr2_int, lfsr3_int))
        ciphertext_output = ciphertext_output + str(int(plaintext_input[i]) ^ key)
        key_output = key_output + str(key)
        # 更新寄存器中的初始状态
        for j in range(3):
            current_lfsr_bin_array[j] = get_next_initial_bin(current_lfsr_bin_array[j], feedback_f_c_bin_array[j])
    # #输出结果
    print("密钥：" + key_output)
    print("密文：" + ciphertext_output)

    # 解密
    ciphertext_input = input("\n-----解密-----\n密文：")
    plaintext_output = ''
    key_output = ''
    # #初始化密钥流生成器
    for i in range(3):
        feedback_f_c_bin_array[i] = feedback_f_c_bin_array[i]
    for i in range(3):
        current_lfsr_bin_array[i] = lfsr_initial_bin_array[i] = lfsr_initial_bin_array[i]
    # #逐位解密
    for i in range(len(ciphertext_input)):
        lfsr1_int = int(current_lfsr_bin_array[0][n_level - 1])
        lfsr2_int = int(current_lfsr_bin_array[1][n_level - 1])
        lfsr3_int = int(current_lfsr_bin_array[2][n_level - 1])
        key = int(geffe_generator(lfsr1_int, lfsr2_int, lfsr3_int))
        plaintext_output = plaintext_output + str(int(ciphertext_input[i]) ^ key)
        key_output = key_output + str(key)
        # 更新寄存器中的初始状态
        for j in range(3):
            current_lfsr_bin_array[j] = get_next_initial_bin(current_lfsr_bin_array[j], feedback_f_c_bin_array[j])
    # #输出结果
    print("密钥：" + key_output)
    print("明文：" + plaintext_output)
    '''
def gen_stream(seed:list,output_len:int):
    return main(seed,output_len)
    