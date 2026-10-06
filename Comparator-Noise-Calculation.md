# Comparator Noise Calculation

<!--
Input: Gaussian decision model and Razavi's 2020 comparator article
Output: Probability-based noise extraction and clearly defined comparison metrics
Position: Statistical companion to StrongARM-Comparator-Design.md
-->


### Gaussian Distribution

For a random variable $x$ with mean $\mu$ and variance $\sigma^2$, the probability density function (PDF) is:

$$x \sim N(\mu, \sigma^2)$$

$$f(x) = \frac{1}{\sqrt{2\pi\sigma^2}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}$$

The cumulative distribution function (CDF) gives the probability that $x \leq k$:

$$\Phi\left(\frac{k-\mu}{\sigma}\right) = P(x \leq k) = \int_{-\infty}^{k} f(x) dx$$

Therefore, the probability that $x > k$ is:

$$P(x > k) = 1 - \Phi\left(\frac{k-\mu}{\sigma}\right)$$

![Gaussian Distribution PDF and CDF](figures/gaussian_distribution.png)

*Figure 1: Gaussian probability density function (left) and cumulative distribution function (right). The CDF shows the probability that noise is below a given threshold voltage.*

![Gaussian with Different Mean](figures/gaussian_different_mu.png)

*Figure 2: Effect of different mean values (μ) on Gaussian distribution with constant σ = 600μV. The three curves show μ = -1mV, 0, and +1mV. Left: PDFs shift horizontally with changing μ. Right: CDFs shift horizontally, with 50% probability always occurring at x = μ.*

### Derivation of Noise Formula

For comparator noise with zero mean ($\mu = 0$):

$$P(x > k) = 1 - \Phi\left(\frac{k}{\sigma}\right)$$

Rearranging:

$$P(x \leq k) = \Phi\left(\frac{k}{\sigma}\right)$$

Taking the inverse CDF on both sides:

$$\frac{k}{\sigma} = \Phi^{-1}(P(x \leq k))$$

Solving for $\sigma$:

$$\sigma = \frac{k}{\Phi^{-1}(P(x \leq k))}$$

**For comparator:** If input signal is $V_{in}$ and output is "1" with probability $P$, then:

$$\sigma_{noise} = \frac{V_{in}}{\Phi^{-1}(P)}$$

This is the formula used in MATLAB: `sigma = Vin/norminv(P)`

This one-point result assumes zero input offset, a Gaussian equivalent input noise, and logical polarity such that positive input increases the probability of output 1. For an offset $V_{OS}$, use

$$P(1\mid V_{in})=\Phi\left(\frac{V_{in}-V_{OS}}{\sigma_{noise}}\right).$$

The 50% crossing locates $V_{OS}$. With two input levels and probabilities strictly between zero and one,

$$\sigma_{noise}=\frac{V_{in,2}-V_{in,1}}{\Phi^{-1}(P_2)-\Phi^{-1}(P_1)}.$$

Avoid extracting noise from $P=0$, $P=1$, or a single point at $P=0.5$. Finite decision records need statistical uncertainty estimates; the approximate binomial standard error is $\sqrt{P(1-P)/K}$ for $K$ independent trials. A 16% minority-decision rate corresponds approximately to an input one noise standard deviation from the offset threshold.

Razavi's *The Design of a Comparator*, pp. 13–14, Figs. 14–15, illustrates this extraction using transient-noise simulations. See [StrongARM Comparator Design](StrongARM-Comparator-Design.md) for the source conditions, offset/noise separation, regeneration and kickback. [Original article](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_4_2020.pdf), [DOI 10.1109/MSSC.2020.3021865](https://doi.org/10.1109/MSSC.2020.3021865).

![Sigma Extraction Method](figures/sigma_extraction.png)

*Figure 3: Illustration of noise extraction from probability measurement. By measuring the input voltage and output probability, we can calculate σ using the inverse Gaussian CDF formula.*

### Comparator Output Probability vs Input

The following figure shows how different input voltages affect the comparator output probability:

![Comparator Scenarios](figures/comparator_scenarios.png)

*Figure 4: Comparator output probability for different input voltages with σ = 600μV. As input voltage increases, the probability of correct output (output=1) increases from 50% to near 100%.*

## Figure of Merit

For a comparison convention based on energy per decision $E_{cmp}$, define

$$\text{FoM}_{E} = \sigma_{noise}^2 E_{cmp}
\quad [(\mu\mathrm{V})^2\cdot\mathrm{nJ}].$$

An optional metric including decision delay is

$$\text{FoM}_{ED} = \sigma_{noise}^2 E_{cmp} T_{cmp}
\quad [(\mu\mathrm{V})^2\cdot\mathrm{nJ}\cdot\mathrm{ns}].$$

These are explicitly defined project comparison metrics, not a claim of a universal FoM standard. Lower values indicate a smaller product under matched conditions. If $P$ denotes average power, use $E_{cmp}=P/f_{cmp}$ with the actual decision rate; $\sigma^2P$ has units of noise variance times power, not energy. Report input common mode, clock rate, delay threshold, load and which drivers are included in the energy measurement.
