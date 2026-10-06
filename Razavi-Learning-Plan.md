# Razavi 文章学习路线

互动入口：本地运行课堂网站后打开 <http://127.0.0.1:4321/learn/razavi/>。
原始目录：<https://www.seas.ucla.edu/brweb/journal.html>。
目录核对日期：2026-10-05；共 148 个 PDF 链接，其中 22 篇为已确认的 Analog Mind 文章。

建议按知识依赖顺序读：**基本电路 → 经典专栏 → Analog Mind 设计文章 → 专题研究论文**。
初学者先配合教材补齐 MOS 工作点、gm/ro、电流镜、差分对、小信号和基本频域分析；额外预留约 18 小时。
文章不要仅按发表时间排列。每篇读三遍：识别问题和连接 → 推导关键关系 → 检查假设和验证边界。

## 推荐起点：ADC / 混合信号

已有模拟电路基础时，推荐每周约 6 小时，合计约 **102 小时 / 17 周**。
时间包含阅读、推导与简化模型验证，是自学估算；完整 PDK 设计与流片需要另行安排。

| 阶段 | 估算 | 阅读和学习产出 |
|---|---:|---|
| 反馈、带宽与噪声预算 | 10 h | 教材复习 + 课堂反馈实验；推导 A/(1+Aβ)，区分带宽、稳定性与积分噪声 |
| 正反馈与再生 | 8 h | The Cross-Coupled Pair Part I → The StrongARM Latch；画连接并解释再生 |
| 采样精度 | 10 h | The Bootstrapped Switch → The Design of a Bootstrapped Sampling Circuit；分别建立 RC、kT/C、失真和时钟预算 |
| 比较器设计 | 10 h | The Design of a Comparator；区分失调、判决噪声、亚稳态与 kickback |
| 离散时间系统 | 12 h | The Switched-Capacitor Integrator → The z-Transform for Analog Designers → The Delta-Sigma Modulator；从电荷守恒与递推式求传递函数 |
| 转换器架构 | 12 h | The Flash ADC → A Tale of Two ADCs → Design Considerations for Interleaved ADCs；比较架构代价并做交织实验 |
| 研究论文精读 | 16 h | A Predictive SAR ADC Architecture；结合 Performance Bounds of ADC-Based Receivers Due to Clock Jitter，复现一个关键结论 |
| 参考、电源与滤波 | 14 h | Bandgap → Low-Voltage Bandgap → LDO → Biquadratic Filter；整理温漂、精度、稳定性和加载限制 |
| 设计审查 | 10 h | Analog Design Experiments With AI Part 1–2；交付规格、架构、预算、独立验证与待验证项 |

每周约 40% 阅读、40% 推导/实验、20% 复盘。阶段可跨周，互动网页会按实际时间预算分配。

## 另外两条路线

- **PLL / 射频时钟**：共同基础 → 环振/晶体/毫米波 VCO → 相位噪声与 jitter → 分频与环路稳定性 → 整数/分数 N 合成 → 低 jitter PLL 精读 → 参考电源 → 设计审查。约 110 小时；每周 6 小时约 19 周。
- **高速链路 / CDR**：共同基础 → TIA 与宽带 I/O → CTLE/DFE → DLL 与相位插值 → CDR → 参考电源 → 设计审查。约 96 小时；每周 6 小时约 16 周。

长系列可留作工具箱：Fifty Applications of the CMOS Inverter Part 1–5 按功能回查。
AI 设计实验建议在能够独立验证之后阅读。

## 完成一个阶段的标准

- 能重画关键连接，并解释每个相位/信号路径。
- 能推导一个关键关系，写清符号、单位和假设。
- 能通过解析计算或仿真检查极限情况，并回答阶段自查问题。

项目有七份原文核验与独立推导笔记，互动页面已链接；其他文章的推荐阅读任务不等同于完成全文研究。
网页记录保存在当前浏览器，可导出带勾选、笔记和每周安排的 Markdown。
