import { Suspense } from 'react';

import EmergencyTrackingRoute from '@/features/emergency/EmergencyTracking';

import Loading from './loading';

export default function Page() {
  return (
    <Suspense fallback={<Loading />}>
      <EmergencyTrackingRoute />
    </Suspense>
  );
}
