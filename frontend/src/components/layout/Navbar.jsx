import React, { useState, useEffect, useRef } from 'react';
import { useLocation, Link, useNavigate } from 'react-router-dom';
import {
  Menu,
  Search,
  Sun,
  Moon,
  ChevronDown,
  Activity,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Bell,
  Check,
  UserCheck
} from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import { useStudent } from '../../context/StudentContext';
import { getSystemStatus } from '../../api/client';
import Avatar from '../ui/Avatar';
import Badge from '../ui/Badge';

export const Navbar = ({ setIsMobileOpen, onOpenCommandPalette }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();
  const { students, currentStudentId, currentStudent, selectStudent } = useStudent();
  const [studentDropdownOpen, setStudentDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Live microservice status polling state
  const [systemHealth, setSystemHealth] = useState({
    status: 'checking',
    skillStatus: 'operational',
    opportunityStatus: 'unknown',
  });

  const checkStatus = async () => {
    try {
      const res = await getSystemStatus();
      const payload = res.data || res;
      const oppStatus = payload.opportunity_service?.status || payload.services?.opportunity_service?.status || 'unknown';
      const skillStat = payload.skill_service?.status || payload.services?.skill_service?.status || 'operational';
      const overall = payload.overall_status || payload.status || 'degraded';
      setSystemHealth({
        status: overall,
        skillStatus: skillStat,
        opportunityStatus: oppStatus,
      });
    } catch {
      setSystemHealth({
        status: 'error',
        skillStatus: 'unreachable',
        opportunityStatus: 'unknown',
      });
    }
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setStudentDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Format breadcrumbs from pathname
  const pathnames = location.pathname.split('/').filter((x) => x);
  const breadcrumbLabels = {
    '': 'Dashboard',
    'skills': 'My Skills',
    'career-goal': 'Career & Skill Gap',
    'roadmap': 'Learning Roadmap',
    'opportunities': 'Opportunities',
    'manage': 'Manage & Admin',
    'system-status': 'System Status',
    'profile': 'Profile & Settings',
  };

  return (
    <header className="sticky top-0 z-30 h-16 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200/80 dark:border-slate-800 px-4 sm:px-6 flex items-center justify-between gap-4">
      {/* Left: Mobile menu toggle & Breadcrumbs */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => setIsMobileOpen(true)}
          className="lg:hidden p-2 rounded-xl text-slate-500 hover:text-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          aria-label="Open mobile navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Breadcrumb Path */}
        <nav className="flex items-center space-x-1.5 text-xs sm:text-sm font-medium">
          <Link
            to="/"
            className="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
          >
            SkillBridge
          </Link>
          {pathnames.length > 0 && (
            <>
              <span className="text-slate-300 dark:text-slate-700">/</span>
              <span className="text-slate-800 dark:text-slate-200 capitalize">
                {breadcrumbLabels[pathnames[0]] || pathnames[0]}
              </span>
            </>
          )}
        </nav>
      </div>

      {/* Right Actions: Command Search, System Indicator, Student Switcher, Theme */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Command Search button */}
        <button
          onClick={onOpenCommandPalette}
          className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800/80 border border-slate-200/60 dark:border-slate-700/60 text-xs text-slate-500 hover:text-slate-900 dark:hover:text-slate-200 transition-colors"
        >
          <Search className="w-3.5 h-3.5 text-slate-400" />
          <span>Search or jump to...</span>
          <kbd className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 shadow-2xs">
            Ctrl K
          </kbd>
        </button>

        {/* Live System Status Pill */}
        <Link
          to="/system-status"
          className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border transition-colors hover:shadow-xs"
          style={{
            backgroundColor:
              systemHealth.status === 'healthy' || systemHealth.status === 'operational'
                ? 'rgba(16, 185, 129, 0.1)'
                : systemHealth.status === 'degraded'
                ? 'rgba(245, 158, 11, 0.1)'
                : 'rgba(244, 63, 94, 0.1)',
            borderColor:
              systemHealth.status === 'healthy' || systemHealth.status === 'operational'
                ? 'rgba(16, 185, 129, 0.3)'
                : systemHealth.status === 'degraded'
                ? 'rgba(245, 158, 11, 0.3)'
                : 'rgba(244, 63, 94, 0.3)',
            color:
              systemHealth.status === 'healthy' || systemHealth.status === 'operational'
                ? '#10b981'
                : systemHealth.status === 'degraded'
                ? '#f59e0b'
                : '#f43f5e',
          }}
          title={`Skill: ${systemHealth.skillStatus} | Opportunity: ${systemHealth.opportunityStatus}`}
        >
          <span
            className="w-2 h-2 rounded-full animate-pulse"
            style={{
              backgroundColor:
                systemHealth.status === 'healthy' || systemHealth.status === 'operational'
                  ? '#10b981'
                  : systemHealth.status === 'degraded'
                  ? '#f59e0b'
                  : '#f43f5e',
            }}
          />
          <span className="capitalize">
            {systemHealth.status === 'healthy' || systemHealth.status === 'operational'
              ? 'Operational'
              : systemHealth.status === 'degraded'
              ? 'Degraded'
              : 'System Alert'}
          </span>
        </Link>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-xl text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
          aria-label="Toggle dark/light theme"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
        </button>

        {/* Active Student Switcher Dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setStudentDropdownOpen((prev) => !prev)}
            className="flex items-center gap-2.5 p-1.5 sm:px-3 sm:py-1.5 rounded-xl border border-slate-200/80 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/60 transition-colors"
            aria-expanded={studentDropdownOpen}
            aria-haspopup="true"
          >
            <Avatar name={currentStudent?.name || 'User'} size="sm" />
            <div className="hidden sm:flex flex-col text-left">
              <span className="text-xs font-semibold text-slate-800 dark:text-slate-100 max-w-[120px] truncate leading-tight">
                {currentStudent?.name || 'Select Student'}
              </span>
              <span className="text-[10px] text-slate-400 leading-none">
                {currentStudent ? `Yr ${currentStudent.year}` : 'Student Switcher'}
              </span>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 ml-0.5" />
          </button>

          {/* Student Dropdown Menu */}
          {studentDropdownOpen && (
            <div className="absolute right-0 mt-2 w-72 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-dropdown py-2 z-50 animate-slide-up">
              <div className="px-4 py-2 border-b border-slate-100 dark:border-slate-800">
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Switch Active Student
                </p>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Dashboard & gap analysis will adjust automatically
                </p>
              </div>

              <div className="max-h-60 overflow-y-auto py-1">
                {(students || []).map((student) => {
                  const isSelected = student.id === currentStudentId;
                  return (
                    <button
                      key={student.id}
                      onClick={() => {
                        selectStudent(student.id);
                        setStudentDropdownOpen(false);
                      }}
                      className={`w-full flex items-center justify-between px-4 py-2.5 text-xs text-left hover:bg-slate-50 dark:hover:bg-slate-800/80 transition-colors ${
                        isSelected ? 'bg-brand-50/70 dark:bg-brand-950/40' : ''
                      }`}
                    >
                      <div className="flex items-center gap-2.5 min-w-0">
                        <Avatar name={student.name} size="sm" />
                        <div className="min-w-0">
                          <p className={`font-semibold truncate ${isSelected ? 'text-brand-600 dark:text-brand-400' : 'text-slate-800 dark:text-slate-200'}`}>
                            {student.name}
                          </p>
                          <p className="text-[11px] text-slate-400 truncate">
                            {student.department} • {student.college}
                          </p>
                        </div>
                      </div>
                      {isSelected && <Check className="w-4 h-4 text-brand-600 shrink-0 ml-2" />}
                    </button>
                  );
                })}
              </div>

              <div className="p-2 border-t border-slate-100 dark:border-slate-800">
                <Link
                  to="/manage"
                  onClick={() => setStudentDropdownOpen(false)}
                  className="flex items-center justify-center gap-1.5 py-1.5 text-xs font-medium text-brand-600 dark:text-brand-400 hover:underline"
                >
                  <UserCheck className="w-3.5 h-3.5" />
                  <span>Manage All Students & Records</span>
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
