import { Navigate, Route, Routes } from 'react-router-dom'

import { AppShell } from '@/components/organisms/app-shell'
import { CampaignsPage } from '@/pages/CampaignsPage'
import { CreatorDatabasePage } from '@/pages/CreatorDatabasePage'
import { DashboardPage } from '@/pages/DashboardPage'
import { SettingsPage } from '@/pages/SettingsPage'

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/campaigns" element={<CampaignsPage />} />
        <Route path="/creators" element={<CreatorDatabasePage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  )
}
