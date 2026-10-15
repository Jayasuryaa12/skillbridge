import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  Target,
  Map,
  Briefcase,
  TrendingUp,
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  Clock,
  Layers,
  ChevronRight,
  ExternalLink,
  Zap,
  Award
} from 'lucide-react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
} from 'recharts';
import { useStudent } from '../context/StudentContext';
import { getDashboardData } from '../api/client';
import Card, { CardHeader, CardContent, CardFooter } from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import Button from '../components/ui/Button';
import ProgressBar from '../components/ui/ProgressBar';
import Skeleton, { CardSkeleton } from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';

export const Dashboard = () => {
  const { currentStudentId, currentStudent, loading: studentLoading } = useStudent();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    const fetchDashboard = async () => {
      if (!currentStudentId) {
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        setError(null);
        const data = await getDashboardData(currentStudentId);
        if (isMounted) {
          setDashboardData(data);
        }
      } catch (err) {
        if (isMounted) {
          console.error('Failed to load dashboard:', err);
          setError('Unable to fetch dashboard metrics. Verify backend microservices are up.');
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchDashboard();
    return () => {
      isMounted = false;
    };
  }, [currentStudentId]);

  if (studentLoading || loading) {
    return (
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <Skeleton width="220px" height="32px" />
            <Skeleton width="340px" height="18px" className="mt-2" />
          </div>
          <Skeleton width="140px" height="40px" />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <CardSkeleton />
          </div>
          <div>
            <CardSkeleton />
          </div>
        </div>
      </div>
    );
  }

  if (error || !dashboardData) {
    return (
      <EmptyState
        icon={<AlertCircle className="w-8 h-8 text-rose-500" />}
        title="Dashboard Unavailable"
        description={error || 'No student data found or microservices are offline.'}
        actionLabel="View System Status"
        onAction={() => window.location.href = '/system-status'}
      />
    );
  }

  const payload = dashboardData?.data || dashboardData || {};
  const student = payload.student || {};
  const career_goal = payload.career || payload.career_goal || {};
  const readinessScore = payload.readiness_score || payload.gap_summary?.readiness_score || 0;
  const matchedCount = payload.skill_counts?.matched ?? payload.gap_summary?.matched_skills?.length ?? 0;
  const developingCount = payload.skill_counts?.developing ?? payload.gap_summary?.developing_skills?.length ?? 0;
  const missingCount = payload.skill_counts?.missing ?? payload.gap_summary?.missing_skills?.length ?? 0;
  const totalRequired = matchedCount + developingCount + missingCount;
  const roadmapProgress = payload.roadmap_progress_percentage ?? 0;
  const roadmap_summary = payload.roadmap_summary || {
    total_stages: payload.roadmap_stages_count || 0,
    completed_stages: Math.round((roadmapProgress / 100) * (payload.roadmap_stages_count || 0)),
  };
  const recommended_opportunities = payload.top_recommendations || payload.recommended_opportunities || [];
  const opportunity_service_status = payload.opportunity_service?.status || payload.opportunity_service_status || 'operational';
  const categoryScores = payload.category_scores || [];
  const topPrioritySkills = payload.top_priority_skills || [];

  // Prepare radar chart data supporting both array of {category, score} and object {category: score}
  let radarData = [];
  if (Array.isArray(categoryScores) && categoryScores.length > 0) {
    radarData = categoryScores.map((item) => ({
      skill: item.category || item.name || 'Skill',
      studentLevel: Math.round(((item.score || 0) / 20) * 10) / 10,
      requiredLevel: 4.5,
      fullMark: 5,
    }));
  } else if (categoryScores && typeof categoryScores === 'object' && Object.keys(categoryScores).length > 0) {
    radarData = Object.entries(categoryScores).map(([cat, score]) => ({
      skill: cat,
      studentLevel: Math.round(((typeof score === 'number' ? score : score?.score || 0) / 20) * 10) / 10,
      requiredLevel: 4.5,
      fullMark: 5,
    }));
  } else if (topPrioritySkills.length > 0) {
    radarData = topPrioritySkills.map((s) => ({
      skill: s.skill || s.name,
      studentLevel: s.current_level || 0,
      requiredLevel: s.target_level || s.required_level || 4,
      fullMark: 5,
    }));
  }

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-brand-900 via-indigo-900 to-slate-900 rounded-3xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/20 border border-brand-400/30 text-brand-200 text-xs font-medium mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI-Driven Skill Analytics</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Welcome back, {student?.name || 'Scholar'}!
          </h1>
          <p className="text-sm sm:text-base text-slate-300 mt-2">
            Targeting{' '}
            <span className="font-semibold text-brand-300">
              {career_goal?.title || 'an aspirational career role'}
            </span>
            . You have closed{' '}
            <span className="font-semibold text-emerald-300">
              {matchedCount} of {totalRequired}
            </span>{' '}
            required competencies.
          </p>
        </div>

        <div className="relative z-10 flex flex-wrap items-center gap-3">
          <Link to="/career-goal">
            <Button variant="secondary" size="md" leftIcon={<Target className="w-4 h-4" />}>
              Switch Goal
            </Button>
          </Link>
          <Link to="/roadmap">
            <Button
              variant="primary"
              size="md"
              leftIcon={<Map className="w-4 h-4" />}
              className="bg-brand-500 hover:bg-brand-400 shadow-glow-brand"
            >
              View Roadmap
            </Button>
          </Link>
        </div>

        {/* Decorative background glow circles */}
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 rounded-full bg-brand-500/20 blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 -mb-12 w-48 h-48 rounded-full bg-sky-500/15 blur-2xl pointer-events-none" />
      </div>

      {/* Downstream degraded notice if opportunity service is down */}
      {opportunity_service_status && opportunity_service_status !== 'operational' && (
        <div className="flex items-center justify-between p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-300 text-sm">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-5 h-5 text-amber-500 shrink-0" />
            <span>
              <strong>Opportunity Service Offline:</strong> Skill recommendations are running in local offline mode. Opportunities will automatically refresh once the service reconnects.
            </span>
          </div>
          <Link to="/system-status" className="font-semibold underline shrink-0 ml-3">
            Inspect
          </Link>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Readiness Score Card */}
        <Card className="p-5 flex flex-col justify-between relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Career Readiness
            </span>
            <div className="w-8 h-8 rounded-xl bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400 flex items-center justify-center">
              <Award className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900 dark:text-slate-100">
              {readinessScore}%
            </span>
            <span className="text-xs text-slate-400">match benchmark</span>
          </div>
          <ProgressBar
            value={readinessScore}
            max={100}
            size="sm"
            color={readinessScore >= 75 ? 'emerald' : readinessScore >= 45 ? 'amber' : 'brand'}
            className="mt-3"
          />
        </Card>

        {/* Matched Skills */}
        <Card className="p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Matched Skills
            </span>
            <div className="w-8 h-8 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400">
              {matchedCount}
            </span>
            <span className="text-xs text-slate-400">of {totalRequired} criteria</span>
          </div>
          <p className="mt-3 text-xs text-slate-500 dark:text-slate-400 truncate">
            Meets or exceeds target level
          </p>
        </Card>

        {/* In-Development & Missing Skills */}
        <Card className="p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Skill Gaps
            </span>
            <div className="w-8 h-8 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 flex items-center justify-center">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-3">
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-extrabold text-amber-500">{developingCount}</span>
              <span className="text-[11px] text-slate-400">in-dev</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-extrabold text-rose-500">{missingCount}</span>
              <span className="text-[11px] text-slate-400">missing</span>
            </div>
          </div>
          <p className="mt-3 text-xs text-slate-500 dark:text-slate-400 truncate">
            Prioritized in learning roadmap
          </p>
        </Card>

        {/* Roadmap Progress */}
        <Card className="p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Roadmap Stages
            </span>
            <div className="w-8 h-8 rounded-xl bg-sky-50 dark:bg-sky-950/60 text-sky-600 dark:text-sky-400 flex items-center justify-center">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900 dark:text-slate-100">
              {roadmap_summary?.completed_stages || 0}
            </span>
            <span className="text-xs text-slate-400">
              / {roadmap_summary?.total_stages || 0} completed
            </span>
          </div>
          <ProgressBar
            value={roadmap_summary?.completed_stages || 0}
            max={roadmap_summary?.total_stages || 1}
            size="sm"
            color="sky"
            className="mt-3"
          />
        </Card>
      </div>

      {/* Main Content Grid: Radar Chart + Skill Gap Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Radar Competency Chart */}
        <Card className="lg:col-span-2">
          <CardHeader
            title="Competency Gap Radar"
            subtitle="Comparing your current verified skill levels vs industry target benchmarks (1-5)"
            action={
              <Link to="/skills">
                <Button variant="ghost" size="sm" rightIcon={<ChevronRight className="w-4 h-4" />}>
                  Manage Skills
                </Button>
              </Link>
            }
          />
          <CardContent className="h-80 sm:h-96">
            {radarData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                  <PolarGrid stroke="#94a3b8" strokeDasharray="3 3" opacity={0.3} />
                  <PolarAngleAxis
                    dataKey="skill"
                    tick={{ fill: '#64748b', fontSize: 12, fontWeight: 500 }}
                  />
                  <PolarRadiusAxis angle={30} domain={[0, 5]} stroke="#94a3b8" opacity={0.4} />
                  <Radar
                    name="Your Level"
                    dataKey="studentLevel"
                    stroke="#4f46e5"
                    fill="#6366f1"
                    fillOpacity={0.4}
                  />
                  <Radar
                    name="Target Level"
                    dataKey="requiredLevel"
                    stroke="#10b981"
                    fill="#34d399"
                    fillOpacity={0.15}
                  />
                  <RechartsTooltip
                    contentStyle={{
                      backgroundColor: 'rgba(15, 23, 42, 0.9)',
                      borderColor: '#334155',
                      borderRadius: '12px',
                      color: '#f8fafc',
                      fontSize: '12px',
                    }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState
                icon={<Target className="w-8 h-8 text-slate-400" />}
                title="No Career Target Set"
                description="Select a career goal to generate an interactive competency radar graph."
                actionLabel="Set Career Goal"
                onAction={() => window.location.href = '/career-goal'}
              />
            )}
          </CardContent>
          <CardFooter>
            <div className="flex flex-wrap items-center gap-4 text-xs font-medium">
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-full bg-brand-500 inline-block" />
                <span className="text-slate-600 dark:text-slate-400">Current Level</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-full bg-emerald-400 inline-block" />
                <span className="text-slate-600 dark:text-slate-400">Required Target</span>
              </div>
            </div>
            <span className="text-xs text-slate-400">Scale: 1 (Novice) to 5 (Expert)</span>
          </CardFooter>
        </Card>

        {/* AI Action Recommendations Card */}
        <Card className="flex flex-col justify-between">
          <div>
            <CardHeader
              title="Next Action Steps"
              subtitle="Algorithmic suggestions for maximum career momentum"
            />
            <CardContent className="space-y-4">
              {/* Highlight 1: Priority missing skill */}
              {missingCount > 0 && (
                <div className="p-3.5 rounded-xl bg-rose-50/60 dark:bg-rose-950/30 border border-rose-200/60 dark:border-rose-900/50">
                  <div className="flex items-center gap-2 text-xs font-semibold text-rose-700 dark:text-rose-400 mb-1">
                    <Zap className="w-3.5 h-3.5" />
                    <span>Critical Prerequisite Missing</span>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-300">
                    <strong>{topPrioritySkills[0]?.skill || topPrioritySkills[0]?.name || 'Key prerequisite'}</strong> is required for your target role. Start Stage 1 in your learning roadmap.
                  </p>
                </div>
              )}

              {/* Highlight 2: In-progress stage */}
              <div className="p-3.5 rounded-xl bg-brand-50/60 dark:bg-brand-950/30 border border-brand-200/60 dark:border-brand-900/50">
                <div className="flex items-center gap-2 text-xs font-semibold text-brand-700 dark:text-brand-300 mb-1">
                  <Map className="w-3.5 h-3.5" />
                  <span>Roadmap Sequencing</span>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-300">
                  Topics are arranged topologically so foundational skills unlock higher-tier frameworks seamlessly.
                </p>
              </div>

              {/* Highlight 3: High match opportunity */}
              <div className="p-3.5 rounded-xl bg-emerald-50/60 dark:bg-emerald-950/30 border border-emerald-200/60 dark:border-emerald-900/50">
                <div className="flex items-center gap-2 text-xs font-semibold text-emerald-700 dark:text-emerald-400 mb-1">
                  <Briefcase className="w-3.5 h-3.5" />
                  <span>Opportunity Discovery</span>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-300">
                  Opportunities weighting rewards programs that teach your missing competencies.
                </p>
              </div>
            </CardContent>
          </div>

          <CardFooter>
            <Link to="/roadmap" className="w-full">
              <Button variant="outline" size="sm" className="w-full" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                Continue Roadmap
              </Button>
            </Link>
          </CardFooter>
        </Card>
      </div>

      {/* Recommended Opportunities Row */}
      <Card>
        <CardHeader
          title="Recommended Opportunities"
          subtitle="Top matching internships, research labs, and roles ranked by your verified skill profile"
          action={
            <Link to="/opportunities">
              <Button variant="ghost" size="sm" rightIcon={<ArrowRight className="w-4 h-4" />}>
                Explore All Opportunities
              </Button>
            </Link>
          }
        />
        <CardContent>
          {recommended_opportunities && recommended_opportunities.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recommended_opportunities.slice(0, 3).map((opp) => (
                <div
                  key={opp.id}
                  className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 hover:shadow-card-hover transition-all flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <Badge variant="brand" size="sm">
                        {opp.type}
                      </Badge>
                      <div className="flex items-center gap-1 text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800">
                        <span>{opp.match_score || 85}% Match</span>
                      </div>
                    </div>
                    <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 line-clamp-1">
                      {opp.title}
                    </h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                      {opp.company} • {opp.location}
                    </p>

                    {/* Skill tags */}
                    <div className="flex flex-wrap gap-1 mt-3">
                      {(opp.required_skills || []).slice(0, 3).map((s, idx) => (
                        <span
                          key={idx}
                          className="text-[11px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300"
                        >
                          {typeof s === 'object' ? s.name : s}
                        </span>
                      ))}
                    </div>

                    {opp.reason && (
                      <p className="mt-3 text-[11px] text-slate-500 dark:text-slate-400 italic bg-slate-50 dark:bg-slate-800/40 p-2 rounded-lg">
                        "{opp.reason}"
                      </p>
                    )}
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                    <span className="text-[11px] text-slate-400">
                      {opp.stipend || opp.deadline || 'Apply online'}
                    </span>
                    {opp.link ? (
                      <a
                        href={opp.link}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs font-semibold text-brand-600 hover:text-brand-500 inline-flex items-center gap-1"
                      >
                        Apply <ExternalLink className="w-3 h-3" />
                      </a>
                    ) : (
                      <Link
                        to={`/opportunities`}
                        className="text-xs font-semibold text-brand-600 hover:text-brand-500"
                      >
                        View Details
                      </Link>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Briefcase className="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                No matching opportunities found right now
              </p>
              <p className="text-xs text-slate-400 mt-1">
                Explore the opportunities catalog or update your skill levels.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
