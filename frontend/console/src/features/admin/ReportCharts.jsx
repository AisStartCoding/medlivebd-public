'use client';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { t, localName } from '@platform/i18n';
import { Card, useLocale } from '@platform/ui';
import { Section, Stat, Empty, formattersFor } from './ReportPrimitives';
const SERIES = 'var(--brand-600)';
const SERIES_NEUTRAL = 'var(--line-strong)';
const SURFACE = 'var(--bg-surface)';
const GRID = 'var(--line-hairline)';
const AXIS_INK = 'var(--ink-muted)';
const LABEL_INK = 'var(--ink-secondary)';
const TICK = { fill: AXIS_INK, fontSize: 'var(--text-caption)' };

const TOOLTIP = {
  contentStyle: {
    background: SURFACE,
    border: '1px solid var(--line-soft)',
    borderRadius: 'var(--radius-sm)',
    color: 'var(--ink-primary)',
    fontSize: 'var(--text-body-sm)',
  },
  labelStyle: { color: LABEL_INK },
  itemStyle: { color: 'var(--ink-primary)' },
};

export function TrendSection({ data, now }) {
  const locale = useLocale();
  const { num, minutes, shortDate } = formattersFor(locale);
  // Every day of the range is on the axis, measured or not. The view only has
  // rows for days a chamber ran, and an axis built from those alone joins
  // Wednesday to Saturday as if Thursday and Friday had been measured — and
  // drops the adoption marker whenever onboarding fell on a day with no
  // chamber, because the marker names a category the axis does not have.
  const byDate = new Map(data.trend.map((point) => [point.date, point]));
  const points = everyDay(data.range.from, data.range.to).map((date) => ({
    label: shortDate(date),
    overrun: byDate.get(date)?.avgOverrunMinutes ?? null,
  }));

  const hasAny = points.some((point) => point.overrun !== null);

  return (
    <Section testId="admin-section-trend" asOf={data.freshness.snapshotAt} now={now}>
      {!hasAny ? (
        <Empty />
      ) : (
        <Card>
          <h2 className="text-title-sm">{t('adminTrendCaption', locale)}</h2>
          <div className="mt-3 h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={points} margin={{ top: 16, right: 16, bottom: 4, left: 0 }}>
                <CartesianGrid stroke={GRID} vertical={false} />
                <XAxis dataKey="label" tick={TICK} tickLine={false} axisLine={false} />
                <YAxis
                  tick={TICK}
                  tickLine={false}
                  axisLine={false}
                  width={40}
                  tickFormatter={(value) => num(value)}
                />
                <Tooltip
                  {...TOOLTIP}
                  cursor={{ stroke: SERIES_NEUTRAL }}
                  formatter={(value) => [minutes(asNumber(value)), t('adminOverrun', locale)]}
                />

                {/* `FR-ADM-02`: "with the live-queue adoption date marked". The
                marker is the point of the chart — it answers whether any
                of this changed anything. Absent, not guessed, for a
                facility with no recorded onboarding. */}
                {data.adoptionDate === null ? null : (
                  <ReferenceLine
                    x={shortDate(data.adoptionDate)}
                    stroke={AXIS_INK}
                    strokeDasharray="4 4"
                    label={{
                      value: t('adminAdoption', locale),
                      position: 'insideTopLeft',
                      fill: LABEL_INK,
                      fontSize: 'var(--text-caption)',
                    }}
                  />
                )}

                {/* Gaps stay gaps. A day with no chamber measured has no
                figure, and a line drawn across it would invent one. */}
                <Line
                  type="linear"
                  dataKey="overrun"
                  stroke={SERIES}
                  strokeWidth={2}
                  // A point on every measured day, so a day measured between
                  // two gaps is still seen. Straight segments: a smoothed
                  // curve overshoots and draws values nobody measured.
                  dot={{ r: 3, fill: SERIES, stroke: SURFACE, strokeWidth: 1 }}
                  activeDot={{ r: 5, stroke: SURFACE, strokeWidth: 2 }}
                  connectNulls={false}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      )}
    </Section>
  );
}

export function LossSection({ data, now }) {
  const locale = useLocale();
  const { num, taka, percent, shortDate } = formattersFor(locale);
  const loss = data.loss;

  // The whole range on the axis, as the trend has: a day with nothing lost
  // and nothing recovered is a day, not a missing column.
  const lossOn = new Map(data.lossByDay.map((row) => [row.date, row]));
  const days =
    data.lossByDay.length === 0
      ? []
      : everyDay(data.range.from, data.range.to).map((date) => ({
          label: shortDate(date),
          lost: lossOn.get(date)?.uncollectedPoisha ?? 0,
          recovered: lossOn.get(date)?.recoveredPoisha ?? 0,
        }));

  return (
    <Section testId="admin-section-loss" asOf={data.freshness.serverTs} now={now}>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Stat label={t('adminNoShows', locale)} value={num(loss.noShowCount)} />
        <Stat label={t('adminForgone', locale)} value={taka(loss.forgonePoisha)} />
        {/* The honest half. A patient who prepaid and did not attend has
            already given the hospital its money, so it is named separately
            rather than counted as a loss. */}
        <Stat label={t('adminPrepaid', locale)} value={taka(loss.prepaidPoisha)} />
        <Stat
          label={t('adminUncollected', locale)}
          value={taka(loss.uncollectedPoisha)}
          testId="admin-uncollected"
        />
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Stat label={t('adminOffersMade', locale)} value={num(loss.offered)} />
        <Stat label={t('adminOffersAccepted', locale)} value={num(loss.accepted)} />
        <Stat
          label={t('adminRecovered', locale)}
          value={taka(loss.recoveredPoisha)}
          tone="brand"
          testId="admin-recovered"
          note={
            loss.recoveryRate === null
              ? null
              : `${t('adminRecoveryRate', locale)} ${percent(loss.recoveryRate)}`
          }
        />
        <Stat label={t('adminNetLoss', locale)} value={taka(loss.netLossPoisha)} />
      </div>

      {days.length === 0 ? null : (
        <Card>
          <h2 className="text-title-sm">{t('adminLossChartTitle', locale)}</h2>
          <div className="mt-3 h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              {/* Side by side, not stacked: a chair freed by a cancellation can
                be recovered on a day with no no-show loss at all, so the two
                are not parts of one whole. */}
              <BarChart data={days} barGap={2} margin={{ top: 8, right: 16, bottom: 4, left: 0 }}>
                <CartesianGrid stroke={GRID} vertical={false} />
                <XAxis dataKey="label" tick={TICK} tickLine={false} axisLine={false} />
                <YAxis
                  tick={TICK}
                  tickLine={false}
                  axisLine={false}
                  width={64}
                  tickFormatter={(value) => taka(value)}
                />
                <Tooltip
                  {...TOOLTIP}
                  cursor={{ fill: 'var(--brand-100)' }}
                  formatter={(value, name) => [taka(asNumber(value)), name]}
                />
                <Legend
                  iconType="square"
                  formatter={(value) => <span style={{ color: LABEL_INK }}>{value}</span>}
                />
                <Bar
                  dataKey="lost"
                  name={t('adminUncollected', locale)}
                  fill={SERIES_NEUTRAL}
                  radius={[4, 4, 0, 0]}
                  maxBarSize={16}
                  isAnimationActive={false}
                />
                <Bar
                  dataKey="recovered"
                  name={t('adminRecovered', locale)}
                  fill={SERIES}
                  radius={[4, 4, 0, 0]}
                  maxBarSize={16}
                  isAnimationActive={false}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      )}
    </Section>
  );
}

export function RevenueBars({ title, slices }) {
  const locale = useLocale();
  const { taka } = formattersFor(locale);
  if (slices.length === 0) return null;

  // Nothing collected is a sentence, not a chart: an axis ticked ৳0.01 to
  // ৳0.04 over empty bars reads as a broken screen (`GR-03`, empty state).
  if (slices.every((slice) => slice.collectedPoisha === 0)) {
    return (
      <Card data-testid="admin-revenue-none">
        <h2 className="text-title-sm">
          {title} · {t('adminCollected', locale)}
        </h2>
        <p className="mt-2 text-body-md text-ink-secondary">{t('adminNothingCollected', locale)}</p>
      </Card>
    );
  }

  const rows = [...slices]
    .sort((a, b) => b.collectedPoisha - a.collectedPoisha)
    .map((slice) => ({
      label: localName(locale, slice.label, slice.labelEn),
      collected: slice.collectedPoisha,
      billed: slice.billedPoisha,
    }));

  return (
    <Card>
      <h2 className="text-title-sm">
        {title} · {t('adminCollected', locale)}
      </h2>
      <div className={`mt-3 w-full ${rows.length > 5 ? 'h-80' : 'h-48'}`}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={rows}
            layout="vertical"
            margin={{ top: 4, right: 24, bottom: 4, left: 8 }}
          >
            <CartesianGrid stroke={GRID} horizontal={false} />
            <XAxis
              type="number"
              tick={TICK}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => taka(value)}
            />
            <YAxis
              type="category"
              dataKey="label"
              tick={{ ...TICK, fill: LABEL_INK }}
              tickLine={false}
              axisLine={false}
              width={170}
            />
            <Tooltip
              {...TOOLTIP}
              cursor={{ fill: 'var(--brand-100)' }}
              formatter={(value) => [taka(asNumber(value)), t('adminCollected', locale)]}
            />
            <Bar
              dataKey="collected"
              fill={SERIES}
              radius={[0, 4, 4, 0]}
              maxBarSize={16}
              isAnimationActive={false}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

export function asNumber(value) {
  return typeof value === 'number' ? value : Number(value);
}

export function everyDay(from, to) {
  const dates = [];
  const at = new Date(`${from}T00:00:00Z`);
  const end = new Date(`${to}T00:00:00Z`);
  while (at.getTime() <= end.getTime()) {
    dates.push(at.toISOString().slice(0, 10));
    at.setUTCDate(at.getUTCDate() + 1);
  }
  return dates;
}
