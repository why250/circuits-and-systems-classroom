import { describe, expect, it } from 'vitest';
import { AMP, mismatch, read, type Reading } from '../src/illustrations/timeinterleave/model';

const fs = 2e9;
const bits = 14;
const options = { fs, analogBandwidth: 20e9, thermalNoiseLsb: 0, jitter: 0 };

/** Independent scalar projection, including the Nyquist endpoint's RMS convention. */
function powerAt(r: Reading, frequency: number): number {
  const n = r.rawData.length;
  let re = 0, im = 0;
  for (let i = 0; i < n; i++) {
    const phase = 2 * Math.PI * frequency * i / fs;
    re += r.rawData[i] * Math.cos(phase);
    im -= r.rawData[i] * Math.sin(phase);
  }
  return (re * re + im * im) / (n * n) * (frequency === fs / 2 ? 1 : 2);
}
const imageDbc = (r: Reading) => 10 * Math.log10(powerAt(r, fs / 2 - r.fin) / powerAt(r, r.fin));

describe('introductory two-channel experiments', () => {
  it('keeps offset at Nyquist as the input moves and agrees with the displayed power convention', () => {
    for (const target of [125e6, 250e6]) {
      const r = read(2, target, mismatch(2, 0, 0.002, 0, 0), bits, 'off', options);
      const peak = Math.sqrt(powerAt(r, fs / 2));
      expect(peak).toBeCloseTo(0.002, 5);
      const measuredDbc = 10 * Math.log10(powerAt(r, fs / 2) / powerAt(r, r.fin));
      const predicted = r.spurs.find(s => s.kind === 'offset')!;
      expect(predicted.freq).toBe(fs / 2);
      expect(measuredDbc).toBeCloseTo(predicted.dbc, 1);
    }
  });

  it('moves the gain image while retaining its relative level', () => {
    const results = [125e6, 250e6].map(target => read(2, target, mismatch(2, 0.005, 0, 0, 0), bits, 'off', options));
    for (const r of results) {
      expect(imageDbc(r)).toBeCloseTo(20 * Math.log10(0.005), 1);
      expect(r.raw.spur).toBe(r.fftPoints / 2 - r.bin);
    }
    expect(imageDbc(results[1]) - imageDbc(results[0])).toBeCloseTo(0, 1);
    const halved = read(2, 125e6, mismatch(2, 0.0025, 0, 0, 0), bits, 'off', options);
    expect(imageDbc(halved) - imageDbc(results[0])).toBeCloseTo(20 * Math.log10(0.5), 1);
  });

  it('measures the skew image from the waveform and verifies the frequency-times-skew rule', () => {
    const low = read(2, 125e6, mismatch(2, 0, 0, 2e-12, 0), bits, 'off', options);
    const high = read(2, 250e6, mismatch(2, 0, 0, 2e-12, 0), bits, 'off', options);
    expect(imageDbc(low)).toBeCloseTo(20 * Math.log10(Math.tan(2 * Math.PI * low.fin * 2e-12)), 1);
    expect(imageDbc(high) - imageDbc(low)).toBeCloseTo(20 * Math.log10(high.fin / low.fin), 1);
    // Keep f_in * skew exactly equal despite coherent-frequency adjustment.
    const smaller = read(2, 250e6, mismatch(2, 0, 0, 2e-12 * low.fin / high.fin, 0), bits, 'off', options);
    expect(imageDbc(smaller)).toBeCloseTo(imageDbc(low), 1);
  });

  it('distinguishes random jitter power from the periodic skew image', () => {
    const r = read(2, 125e6, mismatch(2, 0, 0, 0, 0), bits, 'off', { ...options, jitter: 2e-12 });
    const expectedSnr = -20 * Math.log10(2 * Math.PI * r.fin * 2e-12);
    expect(Math.abs(r.raw.sndr - expectedSnr)).toBeLessThan(0.5);
    const signalPower = powerAt(r, r.fin);
    const totalErrorPower = signalPower / 10 ** (r.raw.sndr / 10);
    expect(powerAt(r, fs / 2 - r.fin)).toBeLessThan(totalErrorPower / 100);
    expect(signalPower).toBeCloseTo(AMP ** 2 / 2, 4);
  });
});
