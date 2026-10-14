import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, LayoutDashboard, Sparkles, Target, Map, Briefcase, SlidersHorizontal, Activity, User, ArrowRight } from 'lucide-react';
import { useStudent } from '../../context/StudentContext';

export const CommandPalette = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();
  const { students, selectStudent } = useStudent();

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
        else onClose(true); // Toggle open
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const quickPages = [
    { title: 'Dashboard', path: '/', icon: LayoutDashboard, category: 'Navigation' },
    { title: 'My Skills & Assessments', path: '/skills', icon: Sparkles, category: 'Navigation' },
    { title: 'Career Goals & Skill Gap', path: '/career-goal', icon: Target, category: 'Navigation' },
    { title: 'Learning Roadmap', path: '/roadmap', icon: Map, category: 'Navigation' },
    { title: 'Opportunity Discovery', path: '/opportunities', icon: Briefcase, category: 'Navigation' },
    { title: 'Admin & Manage Data', path: '/manage', icon: SlidersHorizontal, category: 'Navigation' },
    { title: 'System Status & Architecture', path: '/system-status', icon: Activity, category: 'Navigation' },
    { title: 'Profile & Settings', path: '/profile', icon: User, category: 'Navigation' },
  ];

  const filteredPages = quickPages.filter((p) =>
    p.title.toLowerCase().includes(query.toLowerCase())
  );

  const filteredStudents = (students || []).filter((s) =>
    s.name.toLowerCase().includes(query.toLowerCase()) ||
    s.email.toLowerCase().includes(query.toLowerCase())
  ).slice(0, 4);

  const handleSelectPage = (path) => {
    navigate(path);
    onClose();
  };

  const handleSelectStudent = (id) => {
    selectStudent(id);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 sm:pt-28 px-4">
      <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-xl bg-white dark:bg-slate-900 rounded-2xl shadow-dropdown border border-slate-200 dark:border-slate-800 overflow-hidden z-10 animate-slide-up">
        {/* Search Input */}
        <div className="flex items-center px-4 border-b border-slate-100 dark:border-slate-800">
          <Search className="w-5 h-5 text-slate-400 shrink-0 mr-3" />
          <input
            autoFocus
            type="text"
            placeholder="Type a command, page, or student name..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full py-4 bg-transparent text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 outline-none"
          />
          <kbd className="hidden sm:inline-block text-[11px] font-mono px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 border border-slate-200 dark:border-slate-700">
            ESC
          </kbd>
        </div>

        {/* Results List */}
        <div className="max-h-96 overflow-y-auto p-2 space-y-3">
          {/* Pages */}
          {filteredPages.length > 0 && (
            <div>
              <p className="px-3 py-1 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                Pages & Actions
              </p>
              {filteredPages.map((page) => {
                const Icon = page.icon;
                return (
                  <button
                    key={page.path}
                    onClick={() => handleSelectPage(page.path)}
                    className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-sm text-slate-700 dark:text-slate-200 hover:bg-brand-50 hover:text-brand-700 dark:hover:bg-slate-800/80 transition-colors group"
                  >
                    <div className="flex items-center gap-3">
                      <Icon className="w-4 h-4 text-slate-400 group-hover:text-brand-600" />
                      <span>{page.title}</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                );
              })}
            </div>
          )}

          {/* Students */}
          {filteredStudents.length > 0 && (
            <div>
              <p className="px-3 py-1 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                Switch Active Student
              </p>
              {filteredStudents.map((s) => (
                <button
                  key={s.id}
                  onClick={() => handleSelectStudent(s.id)}
                  className="w-full flex items-center justify-between px-3 py-2 rounded-xl text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-brand-100 dark:bg-brand-900/40 text-brand-700 dark:text-brand-300 text-xs flex items-center justify-center font-bold">
                      {s.name.charAt(0)}
                    </div>
                    <div className="text-left">
                      <span className="font-medium text-xs sm:text-sm">{s.name}</span>
                      <span className="text-xs text-slate-400 ml-2">({s.department})</span>
                    </div>
                  </div>
                  <span className="text-xs text-brand-600 font-medium">Switch</span>
                </button>
              ))}
            </div>
          )}

          {filteredPages.length === 0 && filteredStudents.length === 0 && (
            <div className="py-8 text-center text-sm text-slate-400">
              No results found for "{query}"
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CommandPalette;
