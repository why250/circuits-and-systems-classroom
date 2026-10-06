import catalog from './catalog.json';

export type Track = 'adc' | 'pll' | 'links';
export type Level = 'beginner' | 'foundation';
export interface Stage {
  id: string; title: string; subtitle: string; hours: number; prerequisites: string[];
  articles: string[]; goal: string; tasks: string[]; checkpoint: string;
  hints: string; lab?: { title: string; href: string };
}
export const tracks: Record<Track, { title: string; description: string }> = {
  adc: { title: 'ADC / 混合信号', description: '从采样、比较到离散时间系统与转换器架构。' },
  pll: { title: 'PLL / 射频时钟', description: '从再生、振荡到相位噪声、分频与频率合成。' },
  links: { title: '高速链路 / CDR', description: '从接收前端、通道均衡到相位插值与时钟恢复。' },
};
export const articles = catalog.articles;
export function article(id: string) {
  const result = articles.find(item => item.id === id);
  if (!result) throw new Error(`Unknown article: ${id}`);
  return result;
}
const stages: Record<string, Stage> = {
  entry: { id: 'entry', title: '先补齐器件与电路语言', subtitle: '入门准备', hours: 18, prerequisites: [], articles: ['BR_SSCM_3_2024.pdf'], goal: '能从连接关系写出 KCL，并区分工作点、大信号和小信号。', tasks: ['用教材补齐 MOS 工作区、gm、ro、电流镜与差分对；专栏用于补充例子。', '画出反相器的 DC 转移曲线，标出可作为放大器的区域。', '对一个共源级求增益、输入输出阻抗与主极点。'], checkpoint: '为什么数字反相器也能放大模拟信号？电压增益依赖哪个工作区？', hints: '从转换区的互补跨导与输出电阻解释。器件偏离该工作点后，小信号增益公式不能直接沿用。' },
  feedback: { id: 'feedback', title: '建立反馈、带宽与噪声预算', subtitle: '共同基础 01', hours: 10, prerequisites: [], articles: [], goal: '能把设计指标转化为增益误差、带宽、稳定性和积分噪声要求。', tasks: ['用单极点模型推导 A/(1+Aβ)，区分开环增益与闭环增益。', '比较固定开环参数时，反馈系数改变对增益和带宽的影响。', '复习 PSD、积分噪声与 kT/C；列清单位与单边/双边谱约定。'], checkpoint: '带宽变大后，积分噪声一定减小吗？单极点带宽公式能否证明多极点环路稳定？', hints: '对白噪声，积分频带扩大通常增加总噪声功率；多极点稳定性还需要环路增益和相位裕度。', lab: { title: '反馈增益与带宽实验', href: '/amplifiers/open-loop-and-closed-loop/' } },
  regeneration: { id: 'regeneration', title: '理解正反馈与再生', subtitle: '共同基础 02', hours: 8, prerequisites: ['feedback'], articles: ['BR_Magzine1.pdf', 'BR_Magzine4.pdf'], goal: '能解释交叉耦合结构为何放大小差分，并区分锁存与振荡。', tasks: ['分别画出交叉耦合对与 StrongARM 的关键连接。', '用局部线性模型解释再生的指数增长与适用阶段。', '记录失调、噪声、亚稳态与 kickback 的区别。'], checkpoint: '再生速度快，是否意味着输入等效噪声一定小？', hints: '速度与噪声并不等价。输入信号在再生前的放大、噪声采样、负载与失调都影响判决概率。' },
  sampling: { id: 'sampling', title: '从开关走到采样精度', subtitle: 'ADC 01', hours: 10, prerequisites: ['regeneration'], articles: ['BRSummer15Switch.pdf', 'BR_SSCM_1_2021.pdf'], goal: '能分别建立采样的建立时间、热噪声、失真和时钟误差预算。', tasks: ['先画普通开关的导通电阻随输入变化，再解释自举的作用。', '给定 N 位与采样窗口，估算 RC 建立要求和采样电容量级。', '检查自举电压、体效应与器件端间应力；列出需要 PDK 仿真的项目。'], checkpoint: '自举让 VGS 近似恒定后，是否可以忽略 kT/C 噪声和全部失真？', hints: '自举主要缓解导通电阻随输入变化；寄生、体效应、有限建立、时钟耦合和采样噪声仍然存在。' },
  comparator: { id: 'comparator', title: '把比较器变成可预算的模块', subtitle: 'ADC 02', hours: 10, prerequisites: ['sampling'], articles: ['BR_SSCM_4_2020.pdf'], goal: '能将判决错误率、延迟与 ADC 分辨率联系起来。', tasks: ['按复位、积分/放大、再生三个阶段说明节点变化。', '画输入差分电压对判决概率的曲线，区分噪声与失调。', '比较采样窗口和比较窗口，列出 reset、kickback 与亚稳态的系统约束。'], checkpoint: '重复输入零差分只统计 0/1 比例，能否单独得到噪声 RMS？', hints: '单个输入点不足以分离噪声与失调；应扫描输入、拟合概率曲线，并考虑有限重复次数的不确定度。' },
  discrete: { id: 'discrete', title: '用电荷与 z 域连接电路和系统', subtitle: 'ADC 03', hours: 12, prerequisites: ['comparator'], articles: ['BRWinter17SwCap.pdf', 'BR_SSCM_3_2020.pdf', 'BRSpring16DeltaSigma.pdf'], goal: '能从明确采样时刻的状态方程得到传递函数。', tasks: ['用电荷守恒推导开关电容积分器，标清每个相位。', '先写时域递推，再求 z 域表达式，区分延迟型与非延迟型结构。', '分别写出信号与量化噪声的注入位置；说明线性模型的限制。'], checkpoint: '两个采样值相减是否总能消除噪声？', hints: '噪声抵消依赖相关性。两个独立噪声样本相减会叠加方差；CDS 对不同噪声来源的作用不同。' },
  architecture: { id: 'architecture', title: '比较架构，读懂系统代价', subtitle: 'ADC 04', hours: 12, prerequisites: ['discrete'], articles: ['BRSummer17FlashADC.pdf', 'BRSummer15ADC.pdf', 'BRAug13.pdf'], goal: '能解释 SAR、Flash 与交织方案的速度、能量和精度约束。', tasks: ['分别画出三种架构，标出每次转换的关键操作。', '在 SAR 实验中比较二进制与冗余搜索，解释冗余留下的容错空间。', '在交织实验中分别开启 offset、gain、skew；比较杂散位置与输入频率依赖。'], checkpoint: '固定总采样率时增加交织通道数，会自动提高模拟输入带宽吗？', hints: '每路采样率随之下降，但前端仍需跟踪实际输入；采样时序扩展与模拟带宽是不同约束。', lab: { title: '时间交织 ADC 引导实验', href: '/adc/time-interleaved-adcs/' } },
  adcResearch: { id: 'adcResearch', title: '精读一篇 ADC 研究论文', subtitle: 'ADC 05 · 拓展', hours: 16, prerequisites: ['architecture'], articles: ['Matias_TCAS1_2025.pdf', 'KT_TCAS_2023.pdf'], goal: '能重建论文的关键思想，区分模型预测、仿真与测量。', tasks: ['以 Predictive SAR 为候选；先确认其背景，再重画相对常规 SAR 的改变。', '整理规格、架构、主要限制、验证方法与失效条件。', '结合 jitter 论文，明确输入频率、时钟误差与接收性能的关系；任选一个关键结论复现。'], checkpoint: '论文测得的最佳指标能否直接迁移到自己的工艺、输入频率与负载？', hints: '需要对照工艺、电源、频带、校准条件、测试设置和功耗边界；先建立自己的预算。' },
  oscillators: { id: 'oscillators', title: '从环振到 LC / 毫米波 VCO', subtitle: 'PLL 01', hours: 12, prerequisites: ['regeneration'], articles: ['BR_SSCM_4_2019.pdf', 'BRSpring17CrystalOsc.pdf', 'BR_SSCM_2_2022.pdf'], goal: '能分开讨论起振、小信号条件与稳态振幅限制。', tasks: ['比较环形、晶体与 LC 振荡器的频率选择机制。', '列出负阻、损耗、调谐范围与寄生的设计检查项。', '先用低频等效模型建立直觉，再列出毫米波实现新增的约束。'], checkpoint: '满足小信号起振条件是否就能得到确定的稳态振幅？', hints: '稳态振幅依赖非线性限幅与能量平衡；小信号模型只能支持起振附近的判断。' },
  phaseNoise: { id: 'phaseNoise', title: '建立相位噪声与 jitter 的语言', subtitle: 'PLL 02', hours: 14, prerequisites: ['oscillators'], articles: ['BRMar96.pdf', 'BR_TCAS_2021.pdf'], goal: '能在明确积分频段和谱约定下，把相位噪声转换为时间 jitter。', tasks: ['区分随机 jitter、周期调制与离散 spur。', '注明 SSB / 双边 PSD、积分上下限和载波频率，再计算 RMS jitter。', '整理功耗与 jitter 的设计取舍，用量纲和极限情况检查公式。'], checkpoint: '只有一个 offset 频率处的相位噪声数值，是否足以算总 RMS jitter？', hints: '还需要噪声随频偏的谱形和积分范围，并处理离散 spur；一个谱点不足以决定积分结果。' },
  divider: { id: 'divider', title: '补齐分频与环路动态', subtitle: 'PLL 03', hours: 12, prerequisites: ['phaseNoise'], articles: ['BRFall16TSPC.pdf', 'BR_SSCM_Fall_2022.pdf', 'Ali_TCAS16.pdf'], goal: '能画出 PLL 的线性相位模型并识别采样效应。', tasks: ['从普通触发器分频过渡到高速分频，关注输入摆幅、速度和功耗。', '写出 PFD/CP、滤波器、VCO 与 N 分频的传递关系。', '比较连续时间近似与参考时钟采样条件，说明稳定性分析边界。'], checkpoint: '环路带宽增大，会让参考噪声和 VCO 噪声都更小吗？', hints: '它们经历不同传递函数；通常参考相关噪声在带内传递，而 VCO 噪声在带内受到抑制，最佳带宽需要权衡。' },
  synthesizer: { id: 'synthesizer', title: '组合整数与分数频率合成器', subtitle: 'PLL 04', hours: 14, prerequisites: ['divider'], articles: ['BR_SSCM_2_2023.pdf', 'Yu_JSSC_2022.pdf'], goal: '能解释分数分频产生的误差及噪声整形的作用。', tasks: ['比较整数 N 与分数 N，注明相同参考频率与环路参数。', '比较 accumulator、MASH 与 DTC 补偿；记录 spur 和噪声变化。', '对照文章列出参考源、VCO、分频器和非理想项的噪声预算。'], checkpoint: '噪声整形把误差推到高频，是否意味着总误差能量消失？', hints: '能量不会自动消失；带内改善依赖整形、环路滤波和非理想项，失配及非线性可重新产生带内杂散。', lab: { title: '整数 N / 分数 N PLL 实验', href: '/pll/integer-vs-fractional/' } },
  pllResearch: { id: 'pllResearch', title: '以低 jitter PLL 做研究复现', subtitle: 'PLL 05 · 拓展', hours: 16, prerequisites: ['synthesizer'], articles: ['Yu_JSSC_2023_20fs.pdf'], goal: '能解释指标的测试条件和主要贡献。', tasks: ['整理 20 GHz PLL 的方框图、噪声路径与论文创新。', '核对 jitter 积分频段、功耗边界与 FoM 定义。', '任选一个模型结论复算，提出更换参考频率或电源后的限制。'], checkpoint: '不同论文的 jitter 越小是否就代表电路全面更优？', hints: '应同时比较载波频率、积分范围、功耗、面积、调谐范围与 spur；指标边界必须一致。' },
  frontEnd: { id: 'frontEnd', title: '建立高速接收前端模型', subtitle: '链路 01', hours: 12, prerequisites: ['regeneration'], articles: ['BR_SSCM_1_2019.pdf', 'BR_SSCM_1_2023.pdf', 'BR_SSCM_2_2021.pdf'], goal: '能把信号电流、输入电容、带宽和噪声联系到接收性能。', tasks: ['区分光学 TIA 与电气 I/O 的信号接口和负载。', '推导有限放大器带宽下的跨阻响应，注明增益单位 Ω。', '比较输入电容、反馈电阻和带宽对积分噪声的影响。'], checkpoint: '增大反馈电阻提高跨阻，是否一定改善接收灵敏度？', hints: '必须同时考虑带宽、稳定性、噪声积分、负载和信号码型，不能只看 DC 增益。' },
  equalization: { id: 'equalization', title: '从通道损耗走到 CTLE / DFE', subtitle: '链路 02', hours: 14, prerequisites: ['frontEnd'], articles: ['BR_SSCM_4_2021.pdf', 'BR_SSCM_1_2022.pdf', 'BRFall17DFE.pdf'], goal: '能区分线性频响补偿与基于历史判决的 ISI 抵消。', tasks: ['先用简单低通通道解释 ISI，再比较 CTLE 和 DFE 的作用。', '画出均衡前后的脉冲响应，关注游标与前后游标。', '列出 CTLE 噪声增强与 DFE 误差传播、反馈时序的代价。'], checkpoint: '眼图变开是否足以证明所有输入码型下 BER 达标？', hints: '需要测试码型、采样相位、随机/确定性误差及统计误码；一张眼图不是完整 BER 证据。' },
  timing: { id: 'timing', title: '把相位变成可控的采样时刻', subtitle: '链路 03', hours: 12, prerequisites: ['equalization'], articles: ['BR_SSCM_3_2018.pdf', 'BR_SSCM_4_2023.pdf'], goal: '能解释 DLL、相位插值和 PLL 的不同控制对象。', tasks: ['画出 DLL 与 PLL 的环路，区分延迟和频率的控制。', '说明相位插值的输入相位、权重与输出时刻关系。', '记录插值非线性、相位步长与 jitter 的系统影响。'], checkpoint: '两个相位加权混合，是否总能得到理想线性的时间插值？', hints: '输出零交叉取决于波形、幅度、边沿和负载；线性权重不保证零交叉时刻线性。' },
  recovery: { id: 'recovery', title: '从数据恢复时钟', subtitle: '链路 04', hours: 16, prerequisites: ['timing'], articles: ['BR_SSCM_3_2026.pdf'], goal: '能解释 CDR 怎样利用数据边沿形成误差并调整采样相位。', tasks: ['复习振荡与相位噪声，再读 CDR；辨认相位检测、滤波和时钟控制模块。', '分开讨论频率捕获与锁定附近的相位跟踪。', '注明码型和环路条件，比较 jitter tolerance、transfer 与 generation。'], checkpoint: '缺少数据跳变的长连续码，对时钟恢复提出什么约束？', hints: '相位检测信息减少，需要考虑时钟自由运行误差、保持能力、码型与编码约束。具体行为取决于 CDR 架构。' },
  supplies: { id: 'supplies', title: '补齐参考、电源与滤波模块', subtitle: '跨方向补充', hours: 14, prerequisites: ['feedback'], articles: ['BRSummer16Bandgap.pdf', 'BR_SSCM_3_2021.pdf', 'BR_Magzine5.pdf', 'BR_SSCM_1_2024.pdf'], goal: '能识别偏置、电源和滤波怎样限制系统。', tasks: ['区分带隙参考的温度漂移、绝对精度与启动问题。', '对 LDO 分别考虑 dropout、负载阶跃、稳定性与 PSRR。', '用双二阶滤波器说明 Q、带宽与有限放大器增益的关系。'], checkpoint: '参考源温度曲线很平，是否意味着输出电压绝对值准确？', hints: '温度斜率、工艺偏差、失调和修调是不同问题；温漂小不保证绝对误差小。' },
  capstone: { id: 'capstone', title: '交付自己的设计审查', subtitle: '最终产出', hours: 10, prerequisites: [], articles: ['BR_SSCM_4_2025.pdf', 'BR_SSCM_2_2026.pdf'], goal: '输出一份可追溯、能复现、说明适用范围的设计备忘录。', tasks: ['围绕自己的方向列出规格、架构与关键误差预算。', '选一个关键公式做独立推导，再用解析计算或仿真检查量纲与极限情况。', '读 AI 设计实验作为方法反思；保存来源、假设、失败例子与待验证项。'], checkpoint: 'AI 输出的推导与仿真彼此吻合，能否直接作为独立验证？', hints: '若两者来自相同错误假设，吻合仍可能错误。需要独立模型、原图连接核对和可复现计算。' },
};
const paths: Record<Track, string[]> = {
  adc: ['feedback', 'regeneration', 'sampling', 'comparator', 'discrete', 'architecture', 'adcResearch', 'supplies', 'capstone'],
  pll: ['feedback', 'regeneration', 'oscillators', 'phaseNoise', 'divider', 'synthesizer', 'pllResearch', 'supplies', 'capstone'],
  links: ['feedback', 'regeneration', 'frontEnd', 'equalization', 'timing', 'recovery', 'supplies', 'capstone'],
};
export function route(track: Track, level: Level): Stage[] {
  return [...(level === 'beginner' ? ['entry'] : []), ...paths[track]].map(id => stages[id]);
}
export interface Week { number: number; tasks: { stage: Stage; hours: number }[] }
export function schedule(selected: Stage[], hoursPerWeek: number): Week[] {
  if (!Number.isFinite(hoursPerWeek) || hoursPerWeek <= 0) return [];
  const weeks: Week[] = [];
  for (const stage of selected) {
    let remaining = stage.hours;
    while (remaining > 0) {
      let week = weeks[weeks.length - 1];
      const used = week?.tasks.reduce((sum, task) => sum + task.hours, 0) ?? hoursPerWeek;
      if (!week || used >= hoursPerWeek) { week = { number: weeks.length + 1, tasks: [] }; weeks.push(week); }
      const available = hoursPerWeek - week.tasks.reduce((sum, task) => sum + task.hours, 0);
      const hours = Math.min(remaining, available);
      week.tasks.push({ stage, hours }); remaining -= hours;
    }
  }
  return weeks;
}
export function weekDate(start: string, week: number): string {
  const [year, month, day] = start.split('-').map(Number);
  if (!year || !month || !day) return '';
  const date = new Date(year, month - 1, day + (week - 1) * 7);
  return `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`;
}
