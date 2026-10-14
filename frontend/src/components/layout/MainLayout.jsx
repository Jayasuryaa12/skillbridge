import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Navbar from './Navbar';
import CommandPalette from './CommandPalette';
import ColdStartBanner from './ColdStartBanner';

export const MainLayout = () => {
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col antialiased">
      {/* Sidebar */}
      <Sidebar isMobileOpen={isMobileOpen} setIsMobileOpen={setIsMobileOpen} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col transition-all duration-300 lg:pl-64">
        {/* Sticky Navbar */}
        <Navbar
          setIsMobileOpen={setIsMobileOpen}
          onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
        />

        {/* Cold-Start Waking Up Banner */}
        <ColdStartBanner />

        {/* Page Content View */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto animate-fade-in">
          <Outlet />
        </main>
      </div>

      {/* Global Command Palette */}
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={(shouldOpen) => setIsCommandPaletteOpen(Boolean(shouldOpen))}
      />
    </div>
  );
};

export default MainLayout;
