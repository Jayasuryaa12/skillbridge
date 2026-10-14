import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './context/ToastContext';
import { StudentProvider } from './context/StudentContext';

import MainLayout from './components/layout/MainLayout';
import Dashboard from './pages/Dashboard';
import Skills from './pages/Skills';
import CareerGoal from './pages/CareerGoal';
import Roadmap from './pages/Roadmap';
import Opportunities from './pages/Opportunities';
import Manage from './pages/Manage';
import SystemStatus from './pages/SystemStatus';
import Profile from './pages/Profile';
import NotFound from './pages/NotFound';

// Configure TanStack QueryClient with sensible caching and retry policies
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 1000 * 60 * 2, // 2 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <ToastProvider>
          <StudentProvider>
            <BrowserRouter>
              <Routes>
                <Route path="/" element={<MainLayout />}>
                  <Route index element={<Dashboard />} />
                  <Route path="dashboard" element={<Navigate to="/" replace />} />
                  <Route path="skills" element={<Skills />} />
                  <Route path="career-goal" element={<CareerGoal />} />
                  <Route path="roadmap" element={<Roadmap />} />
                  <Route path="opportunities" element={<Opportunities />} />
                  <Route path="manage" element={<Manage />} />
                  <Route path="system-status" element={<SystemStatus />} />
                  <Route path="profile" element={<Profile />} />
                  <Route path="*" element={<NotFound />} />
                </Route>
              </Routes>
            </BrowserRouter>
          </StudentProvider>
        </ToastProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
