# 电弧炉 PCC 源域数据

本仓库整理物理增强电弧炉时序建模研究中使用的源域数据。原始测量来自 Ugwuagbo 等人在 2021 年发表的数据论文及其补充材料，本仓库维护者为吴童。这里保留原始测量、论文使用的本地选取文件，以及已保存的模型处理数据，并标明三者的区别。

[English documentation](README.en.md)

## 数据概况

- 对齐时段为 2018-11-22 20:01:00 至 2018-11-23 15:00:00，共1140个时间点，间隔60秒。源文件未指定时区，本仓库不作时区转换。
- 三相记为 L1、L2、L3，每相1140行，长表共3420行。这些是同一PCC处的相记录，不是3420个独立时刻。
- 保存的时间划分为 Train、Validation、Test，分别包含798、171、171个时间点，对应2394、513、513行相记录。同一时刻的三相归入相同集合。
- 观测层次为PCC分钟级电能质量统计量，不能当作毫秒级弧端瞬时波形。

## 文件与读取方式

| 位置 | 内容 | 读取说明 |
| --- | --- | --- |
| `data/raw/supplementary_exports/` | 本地保存的四份补充数据CSV导出文件 | 按原字节保留，使用分号分隔。部分文件包含分段导出或重复表头，不作为单一规则矩形表读取 |
| `data/selected_local/` | 实验原先使用的四份 `02.` 前缀文件 | 按原字节保留。其中THD文件还含其他时段，论文窗口以共同时间戳对齐结果为准 |
| `data/processed/pcc_measurements_aligned.csv` | 新整理的纯测量对齐表，1140行、148列 | 逗号分隔、UTF-8编码，保留输入数值字符串，没有插值或生成测量值 |
| `data/processed/data1_physical_model_dataset.csv` | 既有模型处理宽表，1140行、77列 | 同时包含测量量、PCC等效模型输出、残差和质量标记 |
| `data/processed/data1_gru_phase_sequence.csv` | 既有GRU单相序列表，3420行、22列 | 按 `Phase` 与 `TimeIndex` 使用，含六维动态特征和残差标签 |
| `metadata/` | 来源、字段字典、时间划分与文件哈希 | `dataset_manifest.json` 记录范围及转换方式 |
| `tools/verify_dataset.py` | 文件与数据一致性核对脚本 | 仅使用Python标准库，不进行仿真或训练 |

建议从 `pcc_measurements_aligned.csv` 读取测量值，或从 `data1_gru_phase_sequence.csv` 读取已处理的相序列。原始谐波文件的历史名称保留，但名称中的 `1-50` 不代表当前选取文件拥有全部阶次。所选电流文件实际包含2至16次谐波，所选电压文件包含2至25次谐波。完整本地导出文件另行保存在raw目录中，本仓库不将其声称为发布方Excel工作簿的逐字节镜像。

## 特征与标签

序列表的主要动态输入为 `Feature_CassieMayrConductance_S`、`Feature_dCassieMayrConductance_dt_S_per_s`、`Feature_THDI_pct`、`Feature_THDV_pct`、`Feature_CassieMayrPower_kW` 和 `Feature_ReactivePower_kvar`。监督标签为 `Target_ActivePowerResidual_kW`，等于参考有功功率减去模型基线功率。

历史字段名中的 `CassieMayr` 指PCC等效模型生成的特征，不是对真实电弧通道快速状态的直接测量。首个节点的采样间隔和滞后量保留为NaN，其数量列于元数据中，未用人工值填补。这些预计算文件用于既有同节点功率校正研究。一项严格的一步预测实验需要另外检查导数、历史窗口、标定和归一化是否仅使用发布预测时已知的信息。当时刻的 `Reference_RealActivePower_kW` 不能作为预测该时刻残差的输入。

## 核对数据

在仓库根目录执行：

```bash
python tools/verify_dataset.py
```

该脚本核对全部随附文件的SHA-256、1140个连续时间点、三相展开、时间划分、残差标签以及对齐测量值的一致性。数据没有重新训练、仿真、拟合或插值。两份历史模型处理CSV按字节复制，未改变已有实验结果。

## 原始来源与许可

Ugwuagbo, E., Balogun, A., Olajube, A., Omeje, O., Awelewa, A., and Abba-Aliyu, S. Experimental data on power quality assessment at point of common coupling of a steel mill to an electric power grid. *Data in Brief*, 39, 107681, 2021. https://doi.org/10.1016/j.dib.2021.107681

原始文章声明采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可。原始测量的作者和权利归属保持不变，本仓库注明了CSV导出、时段选取、时间对齐及模型处理等变化。详见 [DATA_LICENSE.md](DATA_LICENSE.md) 和 [CITATION.cff](CITATION.cff)。仓库不包含论文正文、作者联系方式、目标设备数据、预测结果或训练权重。
