import React from 'react';
import { Link } from 'react-router-dom';
import { Compass, LayoutDashboard, ArrowLeft, Search } from 'lucide-react';
import Button from '../components/ui/Button';

export const NotFound = () => {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center p-6">
      <div className="w-20 h-20 rounded-3xl bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400 flex items-center justify-center mb-6 shadow-glow-brand">
        <Compass className="w-10 h-10 animate-spin-slow" />
      </div>

      <span className="text-xs font-mono font-bold uppercase tracking-widest text-brand-600 dark:text-brand-400 mb-2">
        Error 404 • Destination Lost
      </span>

      <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight mb-3">
        Page Not Found
      </h1>

      <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md mb-8 leading-relaxed">
        The requested routing URL does not exist on this SkillBridge deployment. Verify the route or navigate back to the primary student dashboard.
      </p>

      <div className="flex flex-wrap items-center justify-center gap-3">
        <Link to="/">
          <Button variant="primary" size="md" leftIcon={<LayoutDashboard className="w-4 h-4" />}>
            Return to Dashboard
          </Button>
        </Link>
        <Link to="/skills">
          <Button variant="outline" size="md" leftIcon={<ArrowLeft className="w-4 h-4" />}>
            Explore Skills
          </Button>
        </Link>
      </div>
    </div>
  );
};

export default NotFound;
