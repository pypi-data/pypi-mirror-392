import sys
from pathlib import Path
import numpy as np

# 设置matplotlib后端为Agg（无GUI）或TkAgg
import matplotlib
matplotlib.use('TkAgg')  # 或者使用 'TkAgg'

import matplotlib.pyplot as plt
import os
# from ibm2ieee.test import test_ibm2ieee
# test_ibm2ieee.main()
# exit()


# --- 基本设置 ---
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def assert_data_equal(label: str, actual, expected, atol: float = 1e-5) -> None:
    """Simple helper to ensure data extracted from SeisData matches source arrays."""
    actual_arr = np.asarray(actual)
    expected_arr = np.asarray(expected)
    if actual_arr.shape != expected_arr.shape:
        raise AssertionError(f"{label} shape mismatch: {actual_arr.shape} vs {expected_arr.shape}")
    diff = np.max(np.abs(actual_arr - expected_arr))
    if diff > atol:
        raise AssertionError(f"{label} mismatch: max diff={diff}")
    print(f"  - {label} 校验通过，shape={actual_arr.shape}, max diff {diff:.2e}")


# 将项目根目录添加到Python路径
project_root = Path(__file__).resolve().parent.parent.parents[0]
sys.path.append(str(project_root))
print(project_root)
from GridSeisPy import SeisData, Horiz, BinField, TraceField, CVDFile
from GridSeisPy.base import io

# CVDFile.SetVDPath()
# sgy = SeisData(r"H:\工区临时文件\BGP_PSTM_pure201909_extend_x-1.sgy").load()

# with open(r"H:\工区临时文件\BGP_PSTM_pure201909_extend_x-1.sgy", 'rb') as f:
#     # 跳过 3200 字节的 EBCDIC 头和 400 字节的二进制头前部
#     f.seek(3224)  # 字节位置 3225 (从1开始计数)
#     format_code_bytes = f.read(2)
    
#     # 尝试大端序解析
#     format_code_big = int.from_bytes(format_code_bytes, byteorder='big')
#     # 尝试小端序解析
#     format_code_little = int.from_bytes(format_code_bytes, byteorder='little')
# sgy.traceData(150)
# i, j = sgy.lineID2ij(649, 479)
# sgy.elems[i, j][[sgy.kX, sgy.kY]]
# k = sgy.field2k(1435.8)
# a = sgy[i, j, k]

# exit()
# horiz: Horiz = sgy.getSeiHoriz()
# horiz[:] = sgy[:, :, 1000:1020].mean(-1)
# # io.savetxt('./test.txt', horiz.dtype.names, horiz.elems[horiz.bool])
# horiz.vis(cmap='seismic', scale_factor=5)
# exit()
# keys, _ = io.loadtxt(r"E:\桌面\SINOPEC-01\test\validation_without_label.txt", usecols=['WELL', 'DEPTH', 'SP', 'GR', 'AC'])
# data = np.zeros((len(_), len(keys)+1))
# data[:, :-1] = _
# wellnames = np.unique((data[:, 0].astype('i4')))
# for wellname in wellnames:
#     welldata = data[data[:, 0] == wellname]
#     io.savetxt(rf'E:\桌面\SINOPEC-01\test\{wellname}.txt', keys[1:] + ['label'], welldata[:, 1:])
#     print(f'{wellname} 已保存')
# print(keys, data)



def main():
    """
    一个自包含的演示脚本，展示 GridSeisPy 的核心功能：
    1. 在内存中创建虚拟地震数据。
    2. 将数据写入一个新的 SEG-Y 文件 (测试写入功能)。
    3. 加载刚刚创建的 SEG-Y 文件 (测试读取功能)。
    4. 对加载的数据进行切片和可视化 (测试处理与可视化功能)。
    """
    # --- 准备工作：定义输出目录和文件名 ---
    output_dir = Path(__file__).resolve().parent / "usage_output"
    output_dir.mkdir(exist_ok=True)
    sgy_path = str(output_dir / "demo_seismic.sgy")

    # --- 步骤 0: 设置工作流会话保存路径 ---
    print(f"--- 步骤 0: 设置工作流会话保存路径 ---")
    CVDFile.SetVDPath(output_dir)
    print(f"  - 会话将保存在: {output_dir.resolve()}\n")
    
    # --- 步骤 1: 创建并保存一个新的 SEG-Y 文件 ---
    # 这个部分对应 README 中的 "Create and Save a New SEG-Y File" 示例
    print(f"--- 步骤 1: 正在创建并保存一个新的 SGY 文件到 '{sgy_path}' ---")
    # 定义虚拟数据的维度
    n_il, n_xl, n_smp = 50, 60, 120
    trace_cnt = n_il * n_xl
    tracesData = np.array([np.sin(np.linspace(0, 2 * np.pi, n_smp)) * (i / trace_cnt)  for i in range(trace_cnt)], dtype='f4').reshape(n_il, n_xl, n_smp)
    SeisData.Data2Segy(sgy_path, inlineIDs=list(range(n_il)), xlineIDs=list(range(n_xl)), smp_seq=list(range(n_smp)), smp_rate=2, tracesData=tracesData, text_header="")
    print("SGY 文件创建成功。\n")

    # --- 步骤 2: 加载数据并保存会话 ---
    # 这个部分对应 README 中的 "Quick Start" 示例
    print(f"--- 步骤 2: 加载SGY文件并保存会话 ---")
    sgy = SeisData(sgy_path).load()
    print("SGY 文件加载成功。")
    print("--- 数据一致性校验: 基础切片 ---")
    volume_from_file = sgy[:, :, :]
    assert_data_equal("全量三维数据", volume_from_file, tracesData)
    inline_idx = sgy.shape[0] // 2
    inline_to_show = sgy.arrInlines[inline_idx]
    inline_slice = sgy.getInline(inline_to_show)
    assert_data_equal("Inline 剖面", inline_slice, tracesData[inline_idx])

    # 将加载并网格化好的对象保存到会话文件
    sgy.Update2VDFile('my_demo_sgy')
    print("  - 会话 'my_demo_sgy' 已保存到磁盘。\n")

    # --- 步骤 3: 从会话恢复对象 ---
    print(f"--- 步骤 3: 模拟新会话, 从磁盘恢复对象 ---")
    sgy = None # 模拟一个全新的环境
    sgy = SeisData.GetObjByName('my_demo_sgy')
    print("  - 从 'my_demo_sgy' 恢复对象成功。")
    print(f"  - 验证恢复的数据维度: {sgy.shape}\n")

    # --- 步骤 4: 在恢复的对象上创建虚拟层位 ---
    print("--- 步骤 4: 在恢复的对象上创建虚拟层位 ---")
    # 在内存中创建层位
    top_horiz = sgy.getSeiHoriz()
    btm_horiz = sgy.getSeiHoriz()
    
    # 构造起伏的层位面
    xx, yy = np.meshgrid(np.linspace(0, 1, sgy.shape[1]), np.linspace(0, 1, sgy.shape[0]))
    top_time = 40 + (np.sin(xx * 2 * np.pi, dtype='f4') + np.cos(yy * 2 * np.pi, dtype='f4')) * 10
    variable_thickness = 15 + 5 * np.sin((xx + yy) * 2 * np.pi)
    btm_time = top_time + variable_thickness
    top_horiz.elems['time'] = top_time
    btm_horiz.elems['time'] = btm_time
    print("虚拟层位创建成功。\n")

    def time_to_sample_idx(time_field):
        idx = np.round((time_field - sgy.smp_start) / sgy.smp_rate).astype(int)
        return np.clip(idx, 0, sgy.smp_cnt - 1)

    # --- 步骤 5: 数据切片与可视化 ---
    print("--- 步骤 5: 演示数据切片与可视化 ---")
    
    # a. 获取剖面（已在一致性校验阶段提取）

    # b. 沿层切片
    slice_along_top = sgy[..., top_horiz]
    
    # c. 获取两层之间的数据中的一个道
    data_between = sgy[..., top_horiz:btm_horiz]
    center_x_idx = sgy.shape[1] // 2
    trace_between = data_between[inline_idx, center_x_idx]

    print("--- 数据一致性校验: 层位/层间提取 ---")
    row_idx = np.arange(sgy.shape[0])[:, None]
    col_idx = np.arange(sgy.shape[1])[None, :]
    top_sample_idx = time_to_sample_idx(top_time)
    btm_sample_idx = time_to_sample_idx(btm_time)
    expected_slice_top = tracesData[row_idx, col_idx, top_sample_idx]
    assert_data_equal("沿顶层位切片", slice_along_top, expected_slice_top)
    expected_trace_between = tracesData[
        inline_idx,
        center_x_idx,
        top_sample_idx[inline_idx, center_x_idx]:btm_sample_idx[inline_idx, center_x_idx]
    ]
    assert_data_equal("层间单道", trace_between, expected_trace_between)

    # d. 可视化
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle("GridSeisPy 'usage.py' 演示")

    axes[0].imshow(inline_slice.T, cmap='seismic', aspect='auto',
                   extent=[sgy.arrXlines[0], sgy.arrXlines[-1], sgy.smp_stop, sgy.smp_start])
    axes[0].set_title(f"剖面: Inline {inline_to_show}")
    axes[0].set_xlabel("Xline")
    axes[0].set_ylabel("Time (ms)")

    im = axes[1].imshow(slice_along_top, cmap='viridis', aspect='auto',
                        extent=[sgy.arrXlines[0], sgy.arrXlines[-1], sgy.arrInlines[-1], sgy.arrInlines[0]])
    axes[1].set_title("沿顶层位切片")
    axes[1].set_xlabel("Xline")
    axes[1].set_ylabel("Inline")
    fig.colorbar(im, ax=axes[1], label="Amplitude")

    time_axis = np.arange(len(trace_between)) * (sgy.smp_rate / 1000) + top_horiz.elems['time'].min()
    axes[2].plot(trace_between, time_axis)
    axes[2].set_title("层间单道")
    axes[2].set_xlabel("Amplitude")
    axes[2].set_ylabel("Relative Time (ms)")
    axes[2].invert_yaxis()
    axes[2].grid(True)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    print("正在显示图像...")
    plt.show()

    # --- 步骤 6: 进阶索引与操作演示 ---
    print("\n--- 步骤 6: 演示进阶索引与层位操作 ---")
    
    # a. 层位运算: 计算两层之间的时间厚度
    time_thickness = btm_horiz - top_horiz
    print(f"  - 计算层位时间厚度, 结果维度: {time_thickness.shape}")

    # b. 坐标转换: 将一个XY坐标转换为网格索引
    #    我们从网格中心取一个坐标点来进行演示
    center_i, center_j = sgy.shape[0] // 2, sgy.shape[1] // 2
    center_x, center_y = sgy.elems[sgy.kX][center_i, center_j], sgy.elems[sgy.kY][center_i, center_j]
    converted_i, converted_j = sgy.xy2ij([center_x], [center_y])
    print(f"  - 坐标转换: XY ({center_x:.2f}, {center_y:.2f}) -> IJ ({converted_i[0]}, {converted_j[0]})")
    
    # c. 高级切片: 使用 np.ogrid 进行局部区域提取
    #    在中心点周围提取一个 11x11 的区域
    area_slice = np.ogrid[center_i - 5:center_i + 6, center_j - 5:center_j + 6]
    regional_data = sgy[area_slice[0], area_slice[1], :]
    print(f"  - 区域提取: 使用 np.ogrid 提取了维度为 {regional_data.shape} 的数据块")
    
    # d. 可视化进阶操作
    fig2, axes2 = plt.subplots(1, 2, figsize=(12, 6))
    fig2.suptitle("进阶功能演示")
    
    # 绘制时间厚度图
    im = axes2[0].imshow(time_thickness.elems[time_thickness.kField], cmap='jet', aspect='auto',
                         extent=[sgy.arrXlines[0], sgy.arrXlines[-1], sgy.arrInlines[-1], sgy.arrInlines[0]])
    axes2[0].set_title("层位时间厚度图 (btm - top)")
    axes2[0].set_xlabel("Xline")
    axes2[0].set_ylabel("Inline")
    fig2.colorbar(im, ax=axes2[0], label="Time Thickness (ms)")
    
    # 绘制区域提取的中心剖面
    regional_inline_slice = regional_data[regional_data.shape[0] // 2, :, :]
    axes2[1].imshow(regional_inline_slice.T, cmap='seismic', aspect='auto',
                    extent=[sgy.arrXlines[center_j-5], sgy.arrXlines[center_j+5], sgy.smp_stop, sgy.smp_start])
    axes2[1].set_title(f"提取区域的中心Inline (大小: {regional_data.shape[0]}x{regional_data.shape[1]})")
    axes2[1].set_xlabel("Xline")
    axes2[1].set_ylabel("Time (ms)")
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    print("正在显示第二张图像...")
    plt.show()

    print("\n'usage.py' 脚本执行完毕。")
    print(f"生成的文件位于: {output_dir.resolve()}")


if __name__ == '__main__':
    main()


