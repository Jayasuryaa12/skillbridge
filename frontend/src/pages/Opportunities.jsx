import React, { useState, useEffect } from 'react';
import {
  Briefcase,
  Search,
  Filter,
  MapPin,
  DollarSign,
  Calendar,
  ExternalLink,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Building,
  Globe,
  SlidersHorizontal,
  ChevronRight,
  TrendingUp
} from 'lucide-react';
import { useStudent } from '../context/StudentContext';
import {
  getOpportunities,
  getRecommendations,
  getOpportunityStats
} from '../api/client';
import Card, { CardHeader, CardContent, CardFooter } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import Input from '../components/ui/Input';
import Modal from '../components/ui/Modal';
import Drawer from '../components/ui/Drawer';
import EmptyState from '../components/ui/EmptyState';
import Skeleton from '../components/ui/Skeleton';

const TYPE_OPTIONS = [
  { value: 'all', label: 'All Categories' },
  { value: 'internship', label: 'Internships' },
  { value: 'project', label: 'Projects' },
  { value: 'hackathon', label: 'Hackathons' },
  { value: 'workshop', label: 'Workshops' },
];

export const Opportunities = () => {
  const { currentStudentId, currentStudent } = useStudent();

  const [mode, setMode] = useState('matched'); // 'matched' or 'all'
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [serviceOffline, setServiceOffline] = useState(false);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [remoteOnly, setRemoteOnly] = useState(false);

  // Drawer / Inspection
  const [selectedOpp, setSelectedOpp] = useState(null);

  const fetchOpportunities = async () => {
    try {
      setLoading(true);
      setServiceOffline(false);

      if (mode === 'matched' && currentStudentId) {
        // Inter-service recommendation endpoint
        const res = await getRecommendations(currentStudentId, {
          type: selectedType !== 'all' ? selectedType : undefined,
          remote: remoteOnly ? true : undefined,
        });
        const rawOpps = res.data?.recommendations || res.recommendations || [];
        setOpportunities(rawOpps.map((o) => ({ ...o, id: o.id || o._id })));
        const oppStatus = res.data?.opportunity_service?.status || res.opportunity_service_status;
        if (oppStatus && oppStatus !== 'operational' && oppStatus !== 'available') {
          setServiceOffline(true);
        }
      } else {
        // Direct opportunities endpoint
        const params = {
          limit: 30,
          search: searchQuery || undefined,
          type: selectedType !== 'all' ? selectedType : undefined,
          remote: remoteOnly ? true : undefined,
        };
        const res = await getOpportunities(params);
        const rawOpps = res.data || res.opportunities || [];
        setOpportunities(rawOpps.map((o) => ({ ...o, id: o.id || o._id })));
      }
    } catch (err) {
      console.warn('Could not fetch opportunities:', err);
      setServiceOffline(true);
      setOpportunities([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOpportunities();
  }, [mode, currentStudentId, selectedType, remoteOnly]);

  const filteredOpportunities = opportunities.filter((opp) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    const titleMatch = opp.title?.toLowerCase().includes(q);
    const companyMatch = opp.company?.toLowerCase().includes(q);
    const skillsMatch = (opp.required_skills || []).some((s) => {
      const name = typeof s === 'object' ? s.name : s;
      return name?.toLowerCase().includes(q);
    });
    return titleMatch || companyMatch || skillsMatch;
  });

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
            Opportunity Discovery
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Discover real internships, research projects, and hackathons ranked by verified skill readiness.
          </p>
        </div>

        {/* Mode Toggle Switch */}
        <div className="flex items-center p-1 bg-slate-100 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 w-fit">
          <button
            onClick={() => setMode('matched')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all select-none ${
              mode === 'matched'
                ? 'bg-white dark:bg-slate-900 text-brand-600 dark:text-brand-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Profile Matches</span>
          </button>
          <button
            onClick={() => setMode('all')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all select-none ${
              mode === 'all'
                ? 'bg-white dark:bg-slate-900 text-brand-600 dark:text-brand-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            <Briefcase className="w-3.5 h-3.5" />
            <span>All Catalog</span>
          </button>
        </div>
      </div>

      {/* Downstream warning if Opportunity Service is down */}
      {serviceOffline && (
        <div className="flex items-center justify-between p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-300 text-sm">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-5 h-5 text-amber-500 shrink-0" />
            <span>
              <strong>Opportunity Service Unreachable:</strong> The standalone opportunity microservice on port 5002 could not be reached. Local fallback response is active.
            </span>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchOpportunities}
            className="border-amber-300 text-amber-800 dark:text-amber-300"
          >
            Retry Ping
          </Button>
        </div>
      )}

      {/* Filters and Search Strip */}
      <Card className="p-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search by role, company, or required skill..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-sm rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-100 placeholder-slate-400 outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            />
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Type selector */}
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="px-3 py-2 rounded-xl text-xs font-semibold bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 outline-none cursor-pointer"
            >
              {TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>

            {/* Remote Checkbox */}
            <label className="flex items-center gap-2 text-xs font-semibold text-slate-600 dark:text-slate-300 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={remoteOnly}
                onChange={(e) => setRemoteOnly(e.target.checked)}
                className="w-4 h-4 rounded text-brand-600 focus:ring-brand-500 rounded-sm"
              />
              <span>Remote Only</span>
            </label>
          </div>
        </div>
      </Card>

      {/* Opportunities Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Skeleton height="220px" />
          <Skeleton height="220px" />
          <Skeleton height="220px" />
        </div>
      ) : filteredOpportunities.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredOpportunities.map((opp) => (
            <Card
              key={opp.id}
              hoverEffect
              onClick={() => setSelectedOpp(opp)}
              className="p-5 flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <Badge variant="brand" size="sm">
                    {opp.type}
                  </Badge>

                  {opp.match_score !== undefined && (
                    <div className="flex items-center gap-1 text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800">
                      <Sparkles className="w-3 h-3" />
                      <span>{opp.match_score}% Match</span>
                    </div>
                  )}
                </div>

                <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors line-clamp-1">
                  {opp.title}
                </h3>
                <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mt-1 flex items-center gap-1.5">
                  <Building className="w-3.5 h-3.5 text-slate-400" />
                  <span>{opp.company}</span>
                </p>

                <p className="mt-3 text-xs text-slate-600 dark:text-slate-300 line-clamp-2">
                  {opp.description}
                </p>

                {/* Match Reason highlight */}
                {opp.reason && (
                  <p className="mt-3 text-[11px] text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-800/40 p-2 rounded-lg italic border border-slate-100 dark:border-slate-800">
                    "{opp.reason}"
                  </p>
                )}

                {/* Skill Pills */}
                <div className="mt-3 flex flex-wrap gap-1">
                  {(opp.required_skills || []).slice(0, 4).map((s, idx) => {
                    const skillName = typeof s === 'object' ? s.name : s;
                    return (
                      <span
                        key={idx}
                        className="text-[11px] px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-medium"
                      >
                        {skillName}
                      </span>
                    );
                  })}
                  {(opp.required_skills?.length || 0) > 4 && (
                    <span className="text-[11px] px-1.5 py-0.5 text-slate-400">
                      +{opp.required_skills.length - 4} more
                    </span>
                  )}
                </div>
              </div>

              {/* Card Bottom Meta */}
              <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-400">
                <span className="flex items-center gap-1">
                  <MapPin className="w-3 h-3" />
                  {opp.remote ? 'Remote' : opp.location || 'Hybrid'}
                </span>
                <span className="font-semibold text-brand-600 hover:text-brand-500 inline-flex items-center gap-1">
                  Inspect <ChevronRight className="w-3 h-3" />
                </span>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={<Briefcase className="w-8 h-8 text-slate-400" />}
          title="No Opportunities Found"
          description="Try broadening your category filter or clearing the search query."
          actionLabel="Clear Filters"
          onAction={() => {
            setSearchQuery('');
            setSelectedType('all');
            setRemoteOnly(false);
          }}
        />
      )}

      {/* Opportunity Detail Drawer */}
      <Drawer
        isOpen={Boolean(selectedOpp)}
        onClose={() => setSelectedOpp(null)}
        title={selectedOpp?.title}
        subtitle={`${selectedOpp?.company} • ${selectedOpp?.location || (selectedOpp?.remote ? 'Remote' : 'On-Site')}`}
        footer={
          <div className="flex items-center justify-between w-full">
            <span className="text-xs text-slate-400">
              {selectedOpp?.deadline ? `Apply by: ${selectedOpp.deadline}` : 'Open Application'}
            </span>
            {selectedOpp?.link ? (
              <a
                href={selectedOpp.link}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-sm transition-colors"
              >
                <span>Apply Externally</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            ) : (
              <Button variant="primary" size="sm" onClick={() => setSelectedOpp(null)}>
                Close
              </Button>
            )}
          </div>
        }
      >
        {selectedOpp && (
          <div className="space-y-6">
            {/* Match Score Banner */}
            {selectedOpp.match_score !== undefined && (
              <div className="p-4 rounded-xl bg-emerald-50/70 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">
                    Match Confidence
                  </span>
                  <span className="text-xl font-extrabold text-emerald-600 dark:text-emerald-400">
                    {selectedOpp.match_score}%
                  </span>
                </div>
                {selectedOpp.reason && (
                  <p className="mt-2 text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
                    {selectedOpp.reason}
                  </p>
                )}
              </div>
            )}

            {/* Overview Attributes */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
                <span className="text-slate-400 block mb-0.5">Type</span>
                <span className="font-semibold text-slate-800 dark:text-slate-200 capitalize">
                  {selectedOpp.type}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
                <span className="text-slate-400 block mb-0.5">Compensation / Stipend</span>
                <span className="font-semibold text-slate-800 dark:text-slate-200">
                  {selectedOpp.stipend || 'Competitive'}
                </span>
              </div>
            </div>

            {/* Role Description */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                Position Details
              </h4>
              <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed whitespace-pre-line">
                {selectedOpp.description}
              </p>
            </div>

            {/* Required Skills Checklist */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                Required Competencies
              </h4>
              <div className="space-y-2">
                {(selectedOpp.required_skills || []).map((skill, idx) => {
                  const sName = typeof skill === 'object' ? skill.name : skill;
                  const sLevel = typeof skill === 'object' ? skill.required_level : null;
                  return (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-700/60 text-xs"
                    >
                      <span className="font-semibold text-slate-800 dark:text-slate-200">
                        {sName}
                      </span>
                      {sLevel && (
                        <span className="text-slate-400">Target Level {sLevel}</span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default Opportunities;
