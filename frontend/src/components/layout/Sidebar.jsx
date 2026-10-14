import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Sparkles,
  Target,
  Map,
  Briefcase,
  SlidersHorizontal,
  Activity,
  User,
  ChevronLeft,
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import Avatar from '../ui/Avatar';
import { useStudent } from '../../context/StudentContext';

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/skills', label: 'My Skills', icon: Sparkles },
  { path: '/career-goal', label: 'Career & Gap Analysis', icon: Target },
  { path: '/roadmap', label: 'Learning Roadmap', icon: Map },
  { path: '/opportunities', label: 'Opportunities', icon: Briefcase },
  { path: '/manage', label: 'Manage & Admin', icon: SlidersHorizontal },
  { path: '/system-status', label: 'System Status', icon: Activity },
  { path: '/profile', label: 'Profile & Settings', icon: User },
];

export const Sidebar = ({ isMobileOpen, setIsMobileOpen }) => {
  const [collapsed, setCollapsed] = useState(() => {
    return localStorage.getItem('skillbridge_sidebar_collapsed') === 'true';
  });
  const { currentStudent } = useStudent();

  const toggleCollapse = () => {
    setCollapsed((prev) => {
      const next = !prev;
      localStorage.setItem('skillbridge_sidebar_collapsed', String(next));
      return next;
    });
  };

  return (
    <>
      {/* Mobile backdrop */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-950/60 backdrop-blur-sm lg:hidden animate-fade-in"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-40 flex flex-col bg-white dark:bg-slate-900 border-r border-slate-200/80 dark:border-slate-800 transition-all duration-300 ease-in-out ${
          collapsed ? 'w-20' : 'w-64'
        } ${isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-slate-100 dark:border-slate-800/80">
          <NavLink
            to="/"
            onClick={() => setIsMobileOpen(false)}
            className="flex items-center gap-3 overflow-hidden select-none"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-brand-500/20 shrink-0">
              <Sparkles className="w-5 h-5" />
            </div>
            {!collapsed && (
              <div className="flex flex-col">
                <span className="font-bold text-base tracking-tight text-slate-900 dark:text-white">
                  Skill<span className="text-brand-600 dark:text-brand-400">Bridge</span>
                </span>
                <span className="text-[10px] uppercase font-semibold tracking-wider text-slate-400 -mt-1">
                  Microservices v2.0
                </span>
              </div>
            )}
          </NavLink>

          <button
            onClick={toggleCollapse}
            className="hidden lg:flex p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            aria-label="Toggle sidebar collapse"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation list */}
        <nav className="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setIsMobileOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 select-none ${
                    isActive
                      ? 'bg-brand-50 text-brand-700 dark:bg-brand-950/60 dark:text-brand-300 shadow-sm border border-brand-200/50 dark:border-brand-800/50 font-semibold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 dark:text-slate-400 dark:hover:text-slate-100 dark:hover:bg-slate-800/60'
                  } ${collapsed ? 'justify-center px-0' : ''}`
                }
                title={collapsed ? item.label : undefined}
              >
                <Icon className="w-5 h-5 shrink-0" />
                {!collapsed && <span className="truncate">{item.label}</span>}
              </NavLink>
            );
          })}
        </nav>

        {/* Bottom Student Profile preview card */}
        <div className="p-3 border-t border-slate-100 dark:border-slate-800/80">
          {currentStudent ? (
            <div
              className={`flex items-center gap-3 p-2 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60 ${
                collapsed ? 'justify-center p-2' : ''
              }`}
            >
              <Avatar name={currentStudent.name} size="md" status="online" />
              {!collapsed && (
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 truncate">
                    {currentStudent.name}
                  </p>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate">
                    {currentStudent.department} • Yr {currentStudent.year}
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-2 text-xs text-slate-400">
              {!collapsed && 'No student active'}
            </div>
          )}
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
