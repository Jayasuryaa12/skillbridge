import React, { useState, useEffect } from 'react';
import {
  Map,
  Sparkles,
  CheckCircle2,
  Clock,
  ExternalLink,
  RotateCw,
  BookOpen,
  Video,
  Code,
  LayoutGrid,
  ListOrdered,
  ChevronRight,
  ArrowRight,
  Award
} from 'lucide-react';
import { useStudent } from '../context/StudentContext';
import { useToast } from '../context/ToastContext';
import {
  getRoadmap,
  generateRoadmap,
  updateRoadmapStage
} from '../api/client';
import Card, { CardHeader, CardContent, CardFooter } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import Tabs from '../components/ui/Tabs';
import ProgressBar from '../components/ui/ProgressBar';
import EmptyState from '../components/ui/EmptyState';
import Skeleton from '../components/ui/Skeleton';

export const Roadmap = () => {
  const { currentStudentId, currentStudent } = useStudent();
  const { showToast } = useToast();

  const [roadmap, setRoadmap] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [updatingStage, setUpdatingStage] = useState(null);
  const [activeView, setActiveView] = useState('timeline'); // 'timeline' or 'kanban'

  const fetchRoadmap = async () => {
    if (!currentStudentId) return;
    try {
      setLoading(true);
      const res = await getRoadmap(currentStudentId);
      setRoadmap(res.data?.roadmap || res.data || res.roadmap || res);
    } catch (err) {
      // 404 means not generated yet
      setRoadmap(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoadmap();
  }, [currentStudentId]);

  const handleGenerate = async () => {
    try {
      setGenerating(true);
      const res = await generateRoadmap(currentStudentId);
      setRoadmap(res.data?.roadmap || res.data || res.roadmap || res);
      showToast({
        type: 'success',
        title: 'Roadmap Synthesized',
        message: 'Topological sort resolved prerequisite dependency graph into sequential stages.',
      });
    } catch (err) {
      console.error('Failed to generate roadmap:', err);
    } finally {
      setGenerating(false);
    }
  };

  const handleUpdateStatus = async (stageOrder, newStatus) => {
    try {
      setUpdatingStage(stageOrder);
      await updateRoadmapStage(currentStudentId, stageOrder, newStatus);
      showToast({
        type: 'success',
        title: 'Milestone Updated',
        message: `Stage ${stageOrder} marked as ${newStatus.replace('_', ' ')}.`,
      });
      await fetchRoadmap();
    } catch (err) {
      console.error('Failed to update stage:', err);
    } finally {
      setUpdatingStage(null);
    }
  };

  const stages = roadmap?.stages || [];
  const completedStages = stages.filter((s) => s.status === 'completed');
  const inProgressStages = stages.filter((s) => s.status === 'in_progress');
  const notStartedStages = stages.filter((s) => !s.status || s.status === 'not_started');
  const totalWeeks = stages.reduce((acc, s) => acc + (s.estimated_weeks || 2), 0);
  const percentComplete = stages.length > 0 ? Math.round((completedStages.length / stages.length) * 100) : 0;

  const getResourceIcon = (type = '') => {
    const t = type.toLowerCase();
    if (t.includes('video') || t.includes('youtube')) return <Video className="w-3.5 h-3.5" />;
    if (t.includes('doc') || t.includes('book')) return <BookOpen className="w-3.5 h-3.5" />;
    return <Code className="w-3.5 h-3.5" />;
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
            Topological Learning Roadmap
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Prerequisite-ordered curriculum mathematically structured using Directed Acyclic Graph (DAG) topological sorting.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Tabs
            tabs={[
              { id: 'timeline', label: 'Timeline', icon: <ListOrdered className="w-4 h-4" /> },
              { id: 'kanban', label: 'Kanban', icon: <LayoutGrid className="w-4 h-4" /> },
            ]}
            activeTab={activeView}
            onChange={setActiveView}
          />
          <Button
            variant="outline"
            size="sm"
            leftIcon={<RotateCw className="w-3.5 h-3.5" />}
            onClick={handleGenerate}
            isLoading={generating}
          >
            Regenerate
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="space-y-4">
          <Skeleton height="100px" />
          <Skeleton height="140px" />
          <Skeleton height="140px" />
        </div>
      ) : stages.length > 0 ? (
        <div className="space-y-6">
          {/* Progress Overview Banner */}
          <Card className="p-6 bg-white dark:bg-slate-900">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Badge variant="brand" size="sm">
                    {stages.length} Milestones
                  </Badge>
                  <span className="text-xs text-slate-400">
                    Est. Duration: ~{totalWeeks} Weeks
                  </span>
                </div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">
                  Curriculum Completion Status: {percentComplete}%
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {completedStages.length} of {stages.length} stages mastered • {inProgressStages.length} active
                </p>
              </div>

              <div className="w-full md:w-72">
                <ProgressBar
                  value={percentComplete}
                  max={100}
                  size="md"
                  color={percentComplete === 100 ? 'emerald' : 'brand'}
                  showLabel
                  label="Pathway Progress"
                />
              </div>
            </div>
          </Card>

          {/* VIEW: Timeline Mode */}
          {activeView === 'timeline' && (
            <div className="relative pl-6 sm:pl-8 space-y-6 before:absolute before:left-3 sm:before:left-4 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-200 dark:before:bg-slate-800">
              {stages.map((stage) => {
                const isCompleted = stage.status === 'completed';
                const isInProgress = stage.status === 'in_progress';
                const isNotStarted = !stage.status || stage.status === 'not_started';

                return (
                  <div key={stage.order} className="relative group">
                    {/* Timeline Node Marker */}
                    <div
                      className={`absolute -left-6 sm:-left-8 top-4 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ring-4 ring-white dark:ring-slate-950 transition-all ${
                        isCompleted
                          ? 'bg-emerald-500 text-white'
                          : isInProgress
                          ? 'bg-brand-600 text-white animate-pulse'
                          : 'bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                      }`}
                    >
                      {isCompleted ? <CheckCircle2 className="w-4 h-4" /> : stage.order}
                    </div>

                    {/* Stage Card */}
                    <Card
                      hoverEffect
                      className={`p-5 sm:p-6 transition-all ${
                        isInProgress
                          ? 'border-brand-300 dark:border-brand-700 ring-2 ring-brand-500/10'
                          : isCompleted
                          ? 'bg-slate-50/50 dark:bg-slate-900/40 opacity-90'
                          : ''
                      }`}
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-slate-800">
                        <div className="flex items-center gap-2.5">
                          <Badge
                            variant={isCompleted ? 'matched' : isInProgress ? 'brand' : 'neutral'}
                            size="md"
                          >
                            Stage {stage.order}
                          </Badge>
                          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                            {stage.skill}
                          </h3>
                        </div>

                        {/* Status change actions */}
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-slate-400 mr-2 flex items-center gap-1">
                            <Clock className="w-3.5 h-3.5" />
                            {stage.estimated_weeks || 2} wks
                          </span>
                          {isNotStarted && (
                            <Button
                              variant="outline"
                              size="sm"
                              isLoading={updatingStage === stage.order}
                              onClick={() => handleUpdateStatus(stage.order, 'in_progress')}
                            >
                              Start Stage
                            </Button>
                          )}
                          {isInProgress && (
                            <Button
                              variant="success"
                              size="sm"
                              isLoading={updatingStage === stage.order}
                              leftIcon={<CheckCircle2 className="w-3.5 h-3.5" />}
                              onClick={() => handleUpdateStatus(stage.order, 'completed')}
                            >
                              Mark Completed
                            </Button>
                          )}
                          {isCompleted && (
                            <Button
                              variant="ghost"
                              size="sm"
                              isLoading={updatingStage === stage.order}
                              onClick={() => handleUpdateStatus(stage.order, 'in_progress')}
                            >
                              Re-open
                            </Button>
                          )}
                        </div>
                      </div>

                      {/* Level Delta info */}
                      <div className="mt-3 flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400">
                        <span>
                          Baseline Level: <strong>L{stage.current_level || 0}</strong>
                        </span>
                        <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
                        <span className="text-brand-600 dark:text-brand-400 font-semibold">
                          Target Competency: <strong>L{stage.target_level || 3}</strong>
                        </span>
                      </div>

                      {/* Curated Resources List */}
                      {stage.resources && stage.resources.length > 0 && (
                        <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/80">
                          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-2">
                            Handpicked Study Materials
                          </span>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {stage.resources.map((res, rIdx) => (
                              <a
                                key={rIdx}
                                href={res.url}
                                target="_blank"
                                rel="noreferrer"
                                className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 hover:bg-brand-50 hover:text-brand-700 dark:hover:bg-slate-800 border border-slate-200/60 dark:border-slate-700/60 text-xs transition-colors group/res"
                              >
                                <div className="flex items-center gap-2 min-w-0">
                                  <span className="text-slate-400 group-hover/res:text-brand-600">
                                    {getResourceIcon(res.type)}
                                  </span>
                                  <span className="font-medium truncate">{res.title}</span>
                                </div>
                                <ExternalLink className="w-3 h-3 text-slate-400 group-hover/res:text-brand-600 shrink-0 ml-2" />
                              </a>
                            ))}
                          </div>
                        </div>
                      )}
                    </Card>
                  </div>
                );
              })}
            </div>
          )}

          {/* VIEW: Kanban Columns Mode */}
          {activeView === 'kanban' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Column 1: Not Started */}
              <div className="space-y-3">
                <div className="flex items-center justify-between px-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                    Not Started ({notStartedStages.length})
                  </span>
                </div>
                <div className="space-y-3">
                  {notStartedStages.map((stage) => (
                    <Card key={stage.order} className="p-4 space-y-2">
                      <div className="flex items-center justify-between">
                        <Badge variant="neutral" size="sm">
                          Stage {stage.order}
                        </Badge>
                        <span className="text-[11px] text-slate-400">{stage.estimated_weeks}w</span>
                      </div>
                      <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                        {stage.skill}
                      </h4>
                      <p className="text-xs text-slate-400">
                        Goal: Level {stage.target_level}
                      </p>
                      <Button
                        variant="secondary"
                        size="sm"
                        className="w-full mt-2"
                        onClick={() => handleUpdateStatus(stage.order, 'in_progress')}
                      >
                        Start Learning
                      </Button>
                    </Card>
                  ))}
                </div>
              </div>

              {/* Column 2: In Progress */}
              <div className="space-y-3">
                <div className="flex items-center justify-between px-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-brand-600 dark:text-brand-400">
                    In Progress ({inProgressStages.length})
                  </span>
                </div>
                <div className="space-y-3">
                  {inProgressStages.map((stage) => (
                    <Card key={stage.order} className="p-4 space-y-2 border-brand-300 dark:border-brand-700">
                      <div className="flex items-center justify-between">
                        <Badge variant="brand" size="sm">
                          Stage {stage.order}
                        </Badge>
                        <span className="text-[11px] text-brand-600 font-semibold">{stage.estimated_weeks}w</span>
                      </div>
                      <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                        {stage.skill}
                      </h4>
                      <Button
                        variant="success"
                        size="sm"
                        className="w-full mt-2"
                        onClick={() => handleUpdateStatus(stage.order, 'completed')}
                      >
                        Mark Done
                      </Button>
                    </Card>
                  ))}
                </div>
              </div>

              {/* Column 3: Completed */}
              <div className="space-y-3">
                <div className="flex items-center justify-between px-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                    Completed ({completedStages.length})
                  </span>
                </div>
                <div className="space-y-3">
                  {completedStages.map((stage) => (
                    <Card key={stage.order} className="p-4 space-y-2 bg-slate-50/50 dark:bg-slate-900/40">
                      <div className="flex items-center justify-between">
                        <Badge variant="matched" size="sm">
                          Stage {stage.order}
                        </Badge>
                        <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                      </div>
                      <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 line-through opacity-70">
                        {stage.skill}
                      </h4>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="w-full mt-2 text-xs"
                        onClick={() => handleUpdateStatus(stage.order, 'in_progress')}
                      >
                        Revisit Stage
                      </Button>
                    </Card>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <EmptyState
          icon={<Map className="w-8 h-8 text-slate-400" />}
          title="No Learning Roadmap Formulated"
          description="Click below to calculate optimal skill sequencing and automatically compile stages based on your target career role."
          actionLabel="Generate Roadmap Now"
          onAction={handleGenerate}
        />
      )}
    </div>
  );
};

export default Roadmap;
