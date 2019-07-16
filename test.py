# coding=utf-8
"""
author = jamon
"""

import time

num = 3
data = [[i+j*num+1 for i in range(0, num)] for j in range(0, num)]


def reverse_row_col(ori_data):
    """
    翻转数组的行列，行做列，列做行
    :param ori_data:
    :return:
    """
    row_len = len(data)  # 原始行数
    col_len = len(data[0])  # 原始列数
    new_data = [[_ for _ in range(row_len)] for _ in range(col_len)]
    for i in range(col_len):
        for j in range(row_len):
            new_data[i][j] = data[j][i]

    return new_data


def reversed(a=[]):
    return [a[i] for i in range(len(a)-1, -1, -1)]


def rotate_array(angle, data):
    """
    核心思想：将原始数组的行做列，列做行产生一个新数组缓存起来，四次旋转的四个结果即为原始数组、缓存的行列转换的数组，
            原始数组每行逆转，缓存的数组每行逆转
    :param angle: int， 旋转角度，取值范围为[90, 180, 270, 360]
    :param data: list, [[], [], ...]
    :return: list, [[], [], []]
    """
    lis = list()
    lis1 = reverse_row_col(data)
    angle = angle % 360  # 数组每旋转360度回到原地
    if 90 == angle:
        for row_index, row in enumerate(lis1):
            lis.append([i for i in reversed(row)])
    elif 180 == angle:
        lis2 = [i for i in reversed(data)]
        for row_index, row in enumerate(lis2):
            lis.append([i for i in reversed(row)])
    elif 270 == angle:
        lis = [i for i in reversed(lis1)]
    else:
        lis = data
    return lis


def rotate_array2(angle, data):
    """
    四种情况：
    1. 90度，依次去每列第i个元素（降序），如第行数为m, 列数为n，则取第n列第i个元素，第n-1列第i个元素…；
    2. 180度，依次去每行第i个元素（降序），如第行数为m, 列数为n，则取第i行第n个元素，第i行第n-1个元素…；
    3. 270度，依次去每列第i个元素（升序），如第行数为m, 列数为n，则取第i列第k个元素，第i+1列第k个元素…；
    4. 360度，原数组不变
    :param angle: int， 旋转角度，取值范围为[90, 180, 270, 360]
    :param data: list, [[], [], ...]
    :return: list, [[], [], []]
    """
    row_len = len(data)    # 原始行数
    col_len = len(data[0]) # 原始列数
    temp = col_len - 1
    temp2 = row_len - 1
    angle = angle % 360  # 数组每旋转360度回到原地

    if 90 == angle:
        result = [[_ for _ in range(row_len)] for _ in range(col_len)]
        for i in range(0, col_len):
            for j in range(temp2, -1, -1):
                result[i][j] = data[temp2-j][i]
    elif 180 == angle:
        result = [[_ for _ in range(col_len)] for _ in range(row_len)]
        for i in range(0, row_len):
            for j in range(temp, -1, -1):
                result[i][j] = data[temp2-i][temp-j]
    elif 270 == angle:
        result = [[_ for _ in range(row_len)] for _ in range(col_len)]
        for i in range(0, col_len):
            for j in range(temp2, -1, -1):
                result[i][j] = data[j][temp-i]
    else:
        result = data

    return result


if __name__ == '__main__':
    data = [[2, 3, 4, 5], [5, 6, 7, 8], [9, 10, 11, 12]]

    s1 = time.time()
    loop_num = 1    # 101 % 4 = 1,最终结果相当于翻转一次
    for angle in [90, 180, 270, 360]:
        s1 = time.time()
        for i in range(loop_num):
            ret = rotate_array(angle, data)
        s2 = time.time()
        # print("x=", x)
        print("\n{} angle rotate_array {} loop took {}s".format(angle, loop_num, s2 - s1))

        s1 = time.time()
        for i in range(loop_num):
            ret2 = rotate_array2(angle, data)
        s2 = time.time()
        print("{} angle rotate_array2  {} loop took {}s".format(angle, loop_num, s2 - s1))

        for r in ret:
            print(r)

        print("")
        for r in ret2:
            print(r)



