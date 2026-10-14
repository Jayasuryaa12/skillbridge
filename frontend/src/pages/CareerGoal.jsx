import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Target,
  Sparkles,
  CheckCircle2,
  TrendingUp,
  AlertCircle,
  ArrowRight,
  Star,
  Layers,
  Map,
  Compass,
  Check,
  Zap,
  Info
} from 'lucide-react';
import { useStudent } from '../context/StudentContext';
import { useToast } from '../context/ToastContext';
import {
  getCareers,
  setCareerGoal,
  getSkillGap,
  generateRoadmap
} from '../api/client';
import Card, { CardHeader, CardContent, CardFooter } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import ProgressBar from '../components/ui/ProgressBar';
import Skeleton from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';

export const CareerGoal = () => {
  const { currentStudentId, currentStudent, refreshCurrentStudent } = useStudent();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [careers, setCareers] = useState([]);
  const [selectedCareerId, setSelectedCareerId] = useState('');
  const [gapData, setGapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [savingGoal, setSavingGoal] = useState(false);
  const [generatingRoadmap, setGeneratingRoadmap] = useState(false);

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setLoading(true);
        const careerRes = await getCareers();
        const rawList = careerRes.data || careerRes.careers || [];
        const list = rawList.map((c) => ({
          ...c,
          id: c.id || c._id,
        }));
        setCareers(list);

        if (currentStudent?.career_goal) {
          setSelectedCareerId(currentStudent.career_goal);
        } else if (list.length > 0) {
          setSelectedCareerId(list[0].id);
        }

        if (currentStudentId) {
          const gapRes = await getSkillGap(currentStudentId);
          setGapData(gapRes.data || gapRes);
        }
      } catch (err) {
        console.error('Failed to load career gap data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchInitialData();
  }, [currentStudentId, currentStudent]);

  const handleSelectGoal = async (careerId) => {
    setSelectedCareerId(careerId);
    try {
      setSavingGoal(true);
      await setCareerGoal(currentStudentId, careerId);
      showToast({
        type: 'success',
        title: 'Career Target Updated',
        message: 'Recalculating competency benchmarks and gap analysis...',
      });
      await refreshCurrentStudent();
      const updatedGap = await getSkillGap(currentStudentId);
      setGapData(updatedGap);
    } catch (err) {
      console.error('Failed to update career goal:', err);
    } finally {
      setSavingGoal(false);
    }
  };

  const handleGenerateRoadmap = async () => {
    try {
      setGeneratingRoadmap(true);
      await generateRoadmap(currentStudentId);
      showToast({
        type: 'success',
        title: 'Roadmap Generated!',
        message: 'Topological sort generated optimal staged learning pathway.',
      });
      navigate('/roadmap');
    } catch (err) {
      console.error('Failed to generate roadmap:', err);
    } finally {
      setGeneratingRoadmap(false);
    }
  };

  const activeCareer = careers.find((c) => c.id === selectedCareerId);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
            Career Targets & Skill Gap Visualizer
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Analyze your readiness against industry benchmarks and isolate high-priority competency deficiencies.
          </p>
        </div>

        <Button
          variant="primary"
          leftIcon={<Map className="w-4 h-4" />}
          onClick={handleGenerateRoadmap}
          isLoading={generatingRoadmap}
          className="shadow-glow-brand"
        >
          Generate Staged Roadmap
        </Button>
      </div>

      {/* Career Goal Selector Strip */}
      <Card className="p-4 sm:p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Select Your Target Career Profile
          </label>
          <span className="text-xs text-slate-400">
            Switching updates gap metrics immediately
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {careers.map((career) => {
            const isSelected = career.id === selectedCareerId;
            return (
              <button
                key={career.id}
                type="button"
                onClick={() => handleSelectGoal(career.id)}
                disabled={savingGoal}
                className={`p-3.5 rounded-xl border text-left transition-all relative ${
                  isSelected
                    ? 'bg-brand-50/80 border-brand-500 text-brand-900 dark:bg-brand-950/60 dark:border-brand-500 dark:text-brand-100 ring-2 ring-brand-500/20 shadow-sm'
                    : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 text-slate-800 dark:text-slate-200'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <h4 className="text-sm font-bold line-clamp-1">{career.title}</h4>
                  {isSelected && <Check className="w-4 h-4 text-brand-600 dark:text-brand-400 shrink-0" />}
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                  {career.description}
                </p>
                <div className="mt-2.5 flex items-center gap-1.5 text-[11px] text-slate-400">
                  <Badge variant="neutral" size="sm">
                    {career.category || 'Tech'}
                  </Badge>
                  <span>{career.required_skills?.length || 0} skills</span>
                </div>
              </button>
            );
          })}
        </div>
      </Card>

      {/* Gap Analysis Summary & Metrics */}
      {loading ? (
        <div className="space-y-4">
          <Skeleton height="120px" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Skeleton height="200px" />
            <Skeleton height="200px" />
            <Skeleton height="200px" />
          </div>
        </div>
      ) : gapData ? (
        <div className="space-y-6">
          {/* Target Overview Card */}
          <Card className="p-6 bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950 text-white border-slate-800 shadow-xl">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div className="max-w-xl">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs uppercase font-bold tracking-wider text-brand-400">
                    Active Career Track
                  </span>
                  <Badge variant="brand" size="sm">
                    {gapData.career?.category || 'Software'}
                  </Badge>
                </div>
                <h2 className="text-2xl font-bold tracking-tight">
                  {gapData.career?.title || activeCareer?.title}
                </h2>
                <p className="text-sm text-slate-300 mt-1.5 leading-relaxed">
                  {gapData.career?.description || activeCareer?.description}
                </p>
              </div>

              {/* Readiness Score dial */}
              <div className="flex flex-col items-center justify-center p-4 rounded-2xl bg-white/5 border border-white/10 shrink-0 min-w-[160px]">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                  Readiness Score
                </span>
                <span className="text-4xl font-extrabold text-white mt-1">
                  {gapData.readiness_score || 0}%
                </span>
                <div className="w-full mt-2">
                  <ProgressBar
                    value={gapData.readiness_score || 0}
                    max={100}
                    size="sm"
                    color={gapData.readiness_score >= 70 ? 'emerald' : 'amber'}
                  />
                </div>
              </div>
            </div>
          </Card>

          {/* 3-Column Detailed Gap Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 1. Matched Skills (Emerald) */}
            <Card className="border-t-4 border-t-emerald-500">
              <CardHeader
                title={`Matched Competencies (${gapData.matched_skills?.length || 0})`}
                subtitle="Your current level meets or surpasses the required benchmark"
              />
              <CardContent className="space-y-3">
                {gapData.matched_skills && gapData.matched_skills.length > 0 ? (
                  gapData.matched_skills.map((skill, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/50 flex flex-col justify-between"
                    >
                      <div className="flex items-start justify-between">
                        <span className="text-sm font-bold text-slate-800 dark:text-slate-100">
                          {skill.name}
                        </span>
                        <Badge variant="matched" size="sm">
                          Verified
                        </Badge>
                      </div>
                      <div className="mt-2 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                        <span>Your: Level {skill.current_level}</span>
                        <span>Target: Level {skill.required_level}</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-400 py-6 text-center">
                    No fully matched skills yet. Progress through your roadmap to meet requirements.
                  </p>
                )}
              </CardContent>
            </Card>

            {/* 2. Developing Skills (Amber) */}
            <Card className="border-t-4 border-t-amber-500">
              <CardHeader
                title={`Developing Skills (${gapData.developing_skills?.length || 0})`}
                subtitle="You possess foundational skills, but require level elevation"
              />
              <CardContent className="space-y-3">
                {gapData.developing_skills && gapData.developing_skills.length > 0 ? (
                  gapData.developing_skills.map((skill, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-100 dark:border-amber-900/50 flex flex-col justify-between"
                    >
                      <div className="flex items-start justify-between">
                        <span className="text-sm font-bold text-slate-800 dark:text-slate-100">
                          {skill.name}
                        </span>
                        <Badge variant="developing" size="sm">
                          +{skill.required_level - skill.current_level} Levels
                        </Badge>
                      </div>
                      <div className="mt-2 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                        <span>Current: L{skill.current_level}</span>
                        <span className="font-semibold text-amber-600">Goal: L{skill.required_level}</span>
                      </div>
                      <ProgressBar
                        value={skill.current_level}
                        max={skill.required_level}
                        size="sm"
                        color="amber"
                        className="mt-2"
                      />
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-400 py-6 text-center">
                    No partially learned skills currently flagged.
                  </p>
                )}
              </CardContent>
            </Card>

            {/* 3. Missing Skills (Rose) */}
            <Card className="border-t-4 border-t-rose-500">
              <CardHeader
                title={`Missing Competencies (${gapData.missing_skills?.length || 0})`}
                subtitle="High priority prerequisite competencies to acquire"
              />
              <CardContent className="space-y-3">
                {gapData.missing_skills && gapData.missing_skills.length > 0 ? (
                  gapData.missing_skills.map((skill, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl bg-rose-50/50 dark:bg-rose-950/20 border border-rose-100 dark:border-rose-900/50 flex flex-col justify-between"
                    >
                      <div className="flex items-start justify-between">
                        <span className="text-sm font-bold text-slate-800 dark:text-slate-100">
                          {skill.name}
                        </span>
                        <Badge variant="missing" size="sm">
                          Target L{skill.required_level}
                        </Badge>
                      </div>
                      {skill.prerequisites && skill.prerequisites.length > 0 && (
                        <div className="mt-2 flex flex-wrap items-center gap-1 text-[11px] text-slate-500">
                          <span className="text-slate-400">Requires:</span>
                          {skill.prerequisites.map((p, pIdx) => (
                            <span key={pIdx} className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                              {p}
                            </span>
                          ))}
                        </div>
                      )}
                      <div className="mt-2.5 flex items-center justify-between text-xs text-slate-400">
                        <span>Importance: {skill.importance || 4}/5</span>
                        <span className="text-rose-500 font-semibold">Priority 1</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-400 py-6 text-center">
                    Outstanding! You have no completely unaddressed skills for this career.
                  </p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      ) : (
        <EmptyState
          icon={<Compass className="w-8 h-8 text-slate-400" />}
          title="Select a Career Track"
          description="Choose one of the career pathways above to run instantaneous skill gap analysis."
        />
      )}
    </div>
  );
};

export default CareerGoal;
