'use client';
import {
  BED_KIND_NAMES,
  bedKindName,
  formatNumber,
  formatTaka,
  t,
  formatAge,
  numeralsFor,
} from '@platform/i18n';
import { Card, FreshnessLine, useLocale } from '@platform/ui';
export function Section({ testId, asOf, now, children }) {
  const locale = useLocale();
  const numerals = numeralsFor(locale);
  return (
    <section className="flex flex-col gap-4" data-testid={testId}>
      <FreshnessLine
        asOf={asOf === null ? null : new Date(asOf)}
        now={now}
        labels={{
          justNow: t('updatedJustNow', locale),
          ago: t('updatedAgo', locale),
          never: t('adminNeverRecorded', locale),
          stale: t('staleWarning', locale),
        }}
        formatMinutes={(value) => formatAge(value, locale, numerals)}
      />
      {children}
    </section>
  );
}

export function Stat({ label, value, tone = 'plain', testId, note = null }) {
  return (
    <Card tone={tone === 'brand' ? 'brand' : 'default'} data-testid={testId}>
      <p className="text-caption text-ink-muted">{label}</p>
      <p
        className="mt-1 text-title-lg tabular-nums"
        data-testid={testId === undefined ? undefined : `${testId}-value`}
      >
        {value}
      </p>
      {note === null ? null : <p className="mt-1 text-caption text-ink-secondary">{note}</p>}
    </Card>
  );
}

export function Empty({ hint }) {
  const locale = useLocale();
  return (
    <Card data-testid="admin-empty">
      <p className="text-body-md text-ink-secondary">{t('adminNothingYet', locale)}</p>
      <p className="mt-1 text-body-sm text-ink-muted">{hint ?? t('adminNothingYetHint', locale)}</p>
    </Card>
  );
}

export function formattersFor(locale) {
  const numerals = numeralsFor(locale);

  function num(value) {
    return formatNumber(value, numerals);
  }

  function taka(poisha) {
    // Chart ticks and tooltips hand back whatever the axis computed, which is
    // not always a whole number of poisha.
    return formatTaka(Math.round(poisha), numerals);
  }

  function minutes(value) {
    if (value === null) return '—';
    return `${num(value)} ${t('minutesShort', locale)}`;
  }

  function hours(value) {
    if (value === null) return '—';
    return `${num(value)} ${t('adminHours', locale)}`;
  }

  function percent(rate) {
    if (rate === null) return '—';
    return `${num(Math.round(rate * 100))}%`;
  }

  /** `DD/MM`, which is as much as an axis tick can carry. */
  function shortDate(iso) {
    const [, month, day] = iso.split('-');
    if (month === undefined || day === undefined) return iso;
    return `${num(Number(day))}/${num(Number(month))}`;
  }

  function bedKind(kind) {
    return kind in BED_KIND_NAMES ? bedKindName(kind, locale) : kind;
  }

  return { num, taka, minutes, hours, percent, shortDate, bedKind };
}
