# 当前课堂项目的实现参考

此文件是项目适配指南，数值和实现以链接目标为准。修改前按需读取相关代码，避免复制另一份模型或完整操作说明。

## 项目约定与位置

- [web/README.md](../../../../web/README.md)：架构、开发命令、添加课题、发布目录、数值验证与访客统计要求的权威说明。
- [package.json](../../../../web/package.json)：当前命令和依赖。`pnpm check` 的 `/dev/null` 重定向在 Windows 默认命令解释器下不可用；必要时分别运行其现有检查项，保持失败可见。不要将检查失败说成通过。
- [Base.astro](../../../../web/src/layouts/Base.astro)：共享主题、导航和页脚；各课题通过 Astro 路由挂载 Svelte 交互组件。
- `web/src/illustrations/<topic>/`：纯计算模型和课题组件；`web/src/components/ui/`、`chart/`：共享控件与图表。
- `web/python/` 与 `web/tests/`：参考模型与数值测试；新增科学模型采用 README 中的 Python 参考约定。已有验证充分的模型可直接复用，增补检查只针对新教学结论或未覆盖条件。

## 用户自己的免费静态托管

- [CLOUDFLARE-PAGES.md](../../../../web/CLOUDFLARE-PAGES.md) 是独立部署的权威操作说明，默认项目 `why250-circuits-classroom`，正式 origin 为 `https://why250-circuits-classroom.pages.dev`。
- 用户请求发布课程时，在 `web/` 中执行 `node scripts/deploy-pages.mjs`；发布前完成相关检查。脚本设置自身的 `SITE_URL`，构建并从独立静态目录上传。先确认已登录用户账号和已有项目，避免重复创建。
- [deploy-pages.mjs](../../../../web/scripts/deploy-pages.mjs) 与 [pages-assets.mjs](../../../../web/scripts/pages-assets.mjs) 负责构建、静态资源整理及上传；不运行上游域名绑定或统计 Worker 部署。未配置独立统计服务时保留访客占位符。
- 验证目标课题的线上 HTTP 响应、实际交互和 canonical origin。若目标课题已经上线且满足本次要求，可核实后直接交付，不必再上传一份相同的部署。

## 已实现的入门样板：时间交织 ADC

入口是 `/adc/time-interleaved-adcs/`，受众了解普通 ADC 和频谱，时间交织从头学。

- [lesson.ts](../../../../web/src/illustrations/timeinterleave/lesson.ts)：学习目标、预测、操作、解释和迁移检查；可参考字段组织内容，无需把每门课强制塞进同一模式。
- [GuidedInterleaving.svelte](../../../../web/src/illustrations/timeinterleave/GuidedInterleaving.svelte)：分步开放控件、预测基线、误差开关、恢复参数、解释展开和理解检查。
- [TimeInterleaveLesson.svelte](../../../../web/src/illustrations/timeinterleave/TimeInterleaveLesson.svelte)：引导模式与原完整实验台的切换；保持组件挂载以保留会话中的状态。当前进度不跨刷新保存。
- [model.ts](../../../../web/src/illustrations/timeinterleave/model.ts)：已有时间交织模型。`read()` 的输出杂散已通过 `outputSpurs()` 转成 FFT 功率约定；不要再对奈奎斯特杂散重复增加 3 dB。
- [timeinterleave-lesson.test.ts](../../../../web/tests/timeinterleave-lesson.test.ts)：独立投影采样数据，验证失调位置、增益幅度、时间失配与频率的乘积规律，以及随机 jitter 的总误差功率。

课程从理想两路到四路，再分别观察失调、增益、固定 skew 和独立随机 jitter。所有入门实验固定总采样率 2 GS/s、14 位量化和公共模拟带宽；只开启当前机制。约 125/250 MHz 的输入会微调到相干频点，翻倍关系须按实际输入频率计算。

可迁移经验：

- “固定总采样率”与“固定每路采样率”的问题刻意分开；迁移题检验学习者是否注意固定条件。
- 比较增益与 skew 时保持误差值不变，用输入频率扫描区分幅度规律；二者的镜像位置可以相同。
- “jitter 形成噪声底”只在本实验独立随机 jitter 模型下使用。周期抖动也会产生边带，不能将课题中的模型特例扩展为普遍规律。
- 通道采样率、总采样率和模拟带宽分别说明。这里复用的正弦前景校准有其适用范围；入门课程尚未执行校准，不因模型包含校准函数就声称已教完校准。
- 窄屏提供实验与图表之间的锚点跳转；通道时刻表与波形颜色对应；解析频点与实测谱线共用实际频率轴。

这个样板经过程序和浏览器验证；其教学效果仍需学习者反馈。后续课题用于检验流程的可迁移性。
