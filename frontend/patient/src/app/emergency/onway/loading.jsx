'use client';

import { tp } from '@platform/i18n';
import { useLocale } from '@platform/ui';

import { TabScreen } from '@/components/TabScreen';

export default function Loading() {
  const locale = useLocale();
  return (
    <TabScreen title={tp('onWayScreenTitle', locale)} back={{ fallback: '/emergency' }}>
      <div className="h-48 rounded-lg bg-sunken" aria-busy="true" data-testid="onway-loading" />
    </TabScreen>
  );
}
