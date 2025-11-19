"""""
模块作用：实现Bicycle LDPC码构造及相关差集/循环矩阵生成工具。
"""""
import numpy as np
from extendedstim.Code.LinearCode.LinearCode import LinearCode
from extendedstim.tools.GaloisTools import generate_matrix
from extendedstim.tools.TypingTools import isinteger


class BicycleCode(LinearCode):
    #%%  CHAPTER：===构造方法===
    def __init__(self, N:int, k:int, M:int, seed:int)->None:
        """""
        input.N：循环矩阵的大小 (偶数)
        input.k：逻辑位数目 (偶数)
        input.M：选取的行数 ( < N/2 ) 用于列权均匀化
        input.seed：随机种子
        """""

        ##  PART：----数据预处理-----
        assert isinteger(N), "N必须是整数"
        assert isinteger(k), "k必须是整数"
        assert isinteger(M), "M必须是整数"
        assert isinteger(seed), "seed必须是整数"

        ##  PART：----生成校验矩阵-----
        np.random.seed(seed)
        H, diff_set = generate_matrix(N, k, M)
        assert np.all(H @ H.T == 0)
        super().__init__(H)