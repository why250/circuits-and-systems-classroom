/** The introductory experiments reuse model.ts; this file holds only the teaching sequence. */
export interface LessonStep {
  title: string;
  aim: string;
  question: string;
  choices: string[];
  answer: number;
  reason: string;
  task: string;
  explanation: string;
  formula: string;
  check: string;
  checkChoices: string[];
  checkAnswer: number;
  checkReason: string;
}

export const lessonSteps: LessonStep[] = [
  {
    title: '轮流采样',
    aim: '把两路 ADC 的采样时刻拼成一条均匀序列。',
    question: '两路各 1 GS/s 的 ADC，采样时刻错开 0.5 ns。合并后的采样率是多少？',
    choices: ['1 GS/s', '2 GS/s', '4 GS/s'], answer: 1,
    reason: '每路每 1 ns 采一次，两路交替后每 0.5 ns 就有一个新样本，因此是 2 GS/s。',
    task: '从两路切换到四路。总采样率保持 2 GS/s，观察每路采样率和同一路样本的间隔。',
    explanation: '总采样率由合并后相邻样本的间隔决定。M 路均匀轮流采样，每路每隔 M 个总时钟周期工作一次。四路时每路只需 0.5 GS/s；各路模拟前端仍需响应输入信号的频率。',
    formula: 'f_channel = f_s / M；t_c[k] = (kM + c) / f_s',
    check: '保持每路 1 GS/s，把两路扩展为四路，总采样率会变成多少？',
    checkChoices: ['1 GS/s', '2 GS/s', '4 GS/s'], checkAnswer: 2,
    checkReason: '这个问题固定的是每路采样率，所以总采样率为 4 × 1 GS/s = 4 GS/s。上面的实验固定的是总采样率。',
  },
  {
    title: '失调失配',
    aim: '识别与输入频率无关的周期误差。',
    question: '两路分别加上 +2 mV 和 −2 mV 的失调。输入频率改变时，失配杂散的位置会怎样？',
    choices: ['跟着输入移动', '固定在总采样率的一半', '只抬高噪声底'], answer: 1,
    reason: '交替的 +Δo、−Δo 每两个样本重复一次，对应总采样率的一半。',
    task: '开启误差，比较约 125 MHz 和 250 MHz 的输入。找到 1 GHz 的杂散，再关闭误差作对照。',
    explanation: '两路失调组成 e[n] = Δo·(−1)ⁿ。这是与输入无关的交替序列，所以它的频率固定在 f_s/2。一般 M 路的相对失调每 M 点重复，可能在 k·f_s/M 产生杂散；各分量的幅度取决于实际通道失调。',
    formula: '两路：e[n] = Δo·(−1)ⁿ → f_spur = f_s/2',
    check: '如果两路都加上相同的 +2 mV，而不是一正一负，会主要出现什么？',
    checkChoices: ['直流偏移', 'f_s/2 的交织杂散', '随机噪声'], checkAnswer: 0,
    checkReason: '共同失调在所有样本上相同，主要表现为 DC。交织杂散来自通道之间的相对失调。',
  },
  {
    title: '增益失配',
    aim: '观察周期增益误差如何搬移输入频谱。',
    question: '两路增益分别为 1 + ε 和 1 − ε。输入从约 125 MHz 变为 250 MHz，交织杂散会怎样？',
    choices: ['保持在 1 GHz', '从约 875 MHz 移到 750 MHz', '从约 125 MHz 移到 250 MHz'], answer: 1,
    reason: '交替增益误差相当于用 (−1)ⁿ 调制输入，产生 f_s/2 ± f_in 的镜像；折叠到第一奈奎斯特区后是 f_s/2 − f_in。',
    task: '保持增益失配不变，切换两种输入频率。比较镜像杂散的位置与 dBc 幅度。',
    explanation: '增益误差与输入相乘：e[n] = ε·(−1)ⁿ·x[n]。对这里的两路、小失配正弦实验，镜像相对载波的幅度约为 ε，因此改变输入频率主要改变杂散位置，其 dBc 幅度基本不变。',
    formula: 'f_spur = f_s/2 − f_in；L_spur ≈ 20 log₁₀|ε| dBc',
    check: '把两路相对增益误差 ε 减半，镜像杂散的 dBc 幅度大约变化多少？',
    checkChoices: ['下降 3 dB', '下降 6 dB', '位置改变，幅度不变'], checkAnswer: 1,
    checkReason: '杂散电压幅度减半，20 log₁₀(1/2) ≈ −6.02 dB；输入频率未变，因此杂散位置不变。',
  },
  {
    title: '时间失配',
    aim: '用输入波形的斜率解释高频输入的敏感性。',
    question: '两路固定采样偏差为 +Δt、−Δt。保持 Δt 不变，把输入频率翻倍，杂散大约怎样变化？',
    choices: ['下降 6 dB', '基本不变', '上升 6 dB'], answer: 2,
    reason: '小时间误差引起的电压误差约为 Δt·dx/dt。正弦的斜率幅度与输入频率成正比，频率翻倍使误差幅度约翻倍。',
    task: '保持时间失配 2 ps，比较约 125 MHz 和 250 MHz 的输入。观察杂散 dBc，再把失配减小或关闭。',
    explanation: '固定通道时间失配也每两点重复，所以镜像位置与增益失配相同。区别在于幅度：小误差条件 2πf_in|Δt| ≪ 1 下，杂散相对载波约为 2πf_in|Δt|。提高输入频率会增加误差；比较这两个频率时增幅接近 6 dB。',
    formula: 'e[n] ≈ Δt_c·x′(t_n)；L_spur ≈ 20 log₁₀(2πf_in|Δt|) dBc',
    check: '输入频率翻倍，同时把时间失配减半，杂散 dBc 幅度大约怎样变化？',
    checkChoices: ['基本不变', '上升 6 dB', '下降 6 dB'], checkAnswer: 0,
    checkReason: '小误差条件下，幅度由 f_in·Δt 决定。一个翻倍、一个减半，乘积保持不变。',
  },
  {
    title: 'Skew 与 jitter',
    aim: '区分固定、周期性的时间失配与随机时钟抖动。',
    question: '把固定通道 skew 换成同样 2 ps RMS 的独立随机 jitter，频谱主要会出现什么变化？',
    choices: ['仍是一条清晰的交织镜像', '出现分散的噪声底', '只有直流偏移'], answer: 1,
    reason: '固定 skew 随通道周期性重复，形成离散杂散；本实验的 jitter 逐样本独立随机，主要形成宽带噪声。',
    task: '在“固定 skew”和“随机 jitter”之间切换，比较离散镜像和噪声底。再切换输入频率，观察 SNDR。',
    explanation: '本实验使用零均值、逐样本独立的高斯 aperture jitter。它引起的电压误差同样与输入斜率有关，但没有固定通道周期。正弦的小抖动近似给出 jitter-only SNR = −20 log₁₀(2πf_inσ_t)。真实时钟也可能含周期抖动或相关相位噪声，频谱形态会不同。',
    formula: 'SNR_jitter ≈ −20 log₁₀(2πf_inσ_t)',
    check: '看到时间误差产生离散边带，就一定能断言是通道 skew 吗？',
    checkChoices: ['能，所有 jitter 都是白噪声', '不能，周期时钟抖动也可能产生离散边带'], checkAnswer: 1,
    checkReason: '频谱特征是诊断线索，还需检查其频率规律以及随通道数、输入频率的变化。独立随机 jitter 只是这里使用的模型。',
  },
];
