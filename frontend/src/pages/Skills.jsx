import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Plus,
  Search,
  Sliders,
  Trash2,
  Edit2,
  CheckCircle2,
  Tag,
  Calendar,
  Layers,
  Filter
} from 'lucide-react';
import { useStudent } from '../context/StudentContext';
import { useToast } from '../context/ToastContext';
import {
  getStudentSkills,
  addStudentSkill,
  updateStudentSkill,
  deleteStudentSkill
} from '../api/client';
import Card, { CardHeader, CardContent } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Modal from '../components/ui/Modal';
import Badge from '../components/ui/Badge';
import ConfirmDialog from '../components/ui/ConfirmDialog';
import EmptyState from '../components/ui/EmptyState';
import Skeleton from '../components/ui/Skeleton';

const LEVEL_LABELS = {
  1: { title: 'Beginner / Novice', desc: 'Basic conceptual understanding', color: 'bg-slate-400' },
  2: { title: 'Elementary', desc: 'Can follow guides and build simple modules', color: 'bg-sky-500' },
  3: { title: 'Intermediate', desc: 'Comfortable solving real problems independently', color: 'bg-brand-500' },
  4: { title: 'Advanced', desc: 'In-depth mastery and system design ability', color: 'bg-amber-500' },
  5: { title: 'Expert / Lead', desc: 'Industry benchmark proficiency & optimization', color: 'bg-emerald-500' },
};

export const Skills = () => {
  const { currentStudentId, currentStudent, refreshCurrentStudent } = useStudent();
  const { showToast } = useToast();

  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');

  // Modal State for Add / Edit
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSkill, setEditingSkill] = useState(null);
  const [skillName, setSkillName] = useState('');
  const [skillLevel, setSkillLevel] = useState(3);
  const [skillCategory, setSkillCategory] = useState('Technical');
  const [saving, setSaving] = useState(false);

  // Delete Confirm State
  const [skillToDelete, setSkillToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const fetchSkills = async () => {
    if (!currentStudentId) return;
    try {
      setLoading(true);
      const res = await getStudentSkills(currentStudentId);
      const list = res.data?.skills || (Array.isArray(res.data) ? res.data : res.skills) || [];
      setSkills(list);
    } catch (err) {
      console.error('Failed to load skills:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSkills();
  }, [currentStudentId]);

  const handleOpenAddModal = () => {
    setEditingSkill(null);
    setSkillName('');
    setSkillLevel(3);
    setSkillCategory('Technical');
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (skill) => {
    setEditingSkill(skill);
    setSkillName(skill.name);
    setSkillLevel(skill.level);
    setSkillCategory(skill.category || 'Technical');
    setIsModalOpen(true);
  };

  const handleSaveSkill = async (e) => {
    e.preventDefault();
    if (!skillName.trim()) {
      showToast({ type: 'warning', title: 'Skill Name Required', message: 'Please input a valid skill name.' });
      return;
    }

    try {
      setSaving(true);
      if (editingSkill) {
        // Update level
        await updateStudentSkill(currentStudentId, editingSkill.name, Number(skillLevel));
        showToast({ type: 'success', title: 'Skill Updated', message: `Updated ${editingSkill.name} to Level ${skillLevel}.` });
      } else {
        // Add new skill
        await addStudentSkill(currentStudentId, {
          name: skillName.trim(),
          level: Number(skillLevel),
          category: skillCategory,
        });
        showToast({ type: 'success', title: 'Skill Added', message: `Added ${skillName} at Level ${skillLevel}.` });
      }

      setIsModalOpen(false);
      await fetchSkills();
      await refreshCurrentStudent();
    } catch (err) {
      console.error('Error saving skill:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!skillToDelete) return;
    try {
      setDeleting(true);
      await deleteStudentSkill(currentStudentId, skillToDelete.name);
      showToast({ type: 'success', title: 'Skill Removed', message: `Removed ${skillToDelete.name} from profile.` });
      setSkillToDelete(null);
      await fetchSkills();
      await refreshCurrentStudent();
    } catch (err) {
      console.error('Error deleting skill:', err);
    } finally {
      setDeleting(false);
    }
  };

  const filteredSkills = skills.filter((s) => {
    const matchesSearch = s.name.toLowerCase().includes(searchQuery.toLowerCase());
    if (selectedFilter === 'all') return matchesSearch;
    if (selectedFilter === 'advanced') return matchesSearch && s.level >= 4;
    if (selectedFilter === 'intermediate') return matchesSearch && s.level === 3;
    if (selectedFilter === 'beginner') return matchesSearch && s.level <= 2;
    return matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header View */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
            My Verified Skills
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Manage your verified competencies, assess your mastery levels, and prepare for gap analysis.
          </p>
        </div>
        <Button
          variant="primary"
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={handleOpenAddModal}
        >
          Add New Skill
        </Button>
      </div>

      {/* Filter and Search Bar */}
      <Card className="p-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search skills by name (e.g., Python, Docker)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-sm rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-100 placeholder-slate-400 outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            />
          </div>

          <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
            {['all', 'advanced', 'intermediate', 'beginner'].map((filterKey) => (
              <button
                key={filterKey}
                onClick={() => setSelectedFilter(filterKey)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold uppercase tracking-wider transition-colors select-none ${
                  selectedFilter === filterKey
                    ? 'bg-brand-600 text-white shadow-sm'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
                }`}
              >
                {filterKey}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Skills Grid */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <Skeleton height="160px" />
          <Skeleton height="160px" />
          <Skeleton height="160px" />
          <Skeleton height="160px" />
        </div>
      ) : filteredSkills.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredSkills.map((skill) => {
            const levelInfo = LEVEL_LABELS[skill.level] || LEVEL_LABELS[3];
            return (
              <Card
                key={skill.name}
                hoverEffect
                className="p-5 flex flex-col justify-between group"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
                      {skill.name}
                    </h3>
                    <div className="flex items-center gap-1 opacity-80 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => handleOpenEditModal(skill)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-brand-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                        title="Edit skill level"
                        aria-label="Edit skill level"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => setSkillToDelete(skill)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                        title="Delete skill"
                        aria-label="Delete skill"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  {/* Level visualization */}
                  <div className="mt-3 flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-700 dark:text-slate-300">
                      Level {skill.level}/5
                    </span>
                    <span className="text-slate-400 text-[11px] font-medium">
                      {levelInfo.title}
                    </span>
                  </div>

                  {/* Level Pips */}
                  <div className="grid grid-cols-5 gap-1.5 mt-1.5">
                    {[1, 2, 3, 4, 5].map((lvl) => (
                      <div
                        key={lvl}
                        className={`h-2 rounded-full transition-all ${
                          lvl <= skill.level ? levelInfo.color : 'bg-slate-200 dark:bg-slate-800'
                        }`}
                      />
                    ))}
                  </div>

                  <p className="mt-2.5 text-[11px] text-slate-500 dark:text-slate-400">
                    {levelInfo.desc}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
                  <span className="inline-flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {skill.updated_at ? new Date(skill.updated_at).toLocaleDateString() : 'Active'}
                  </span>
                  <Badge variant="neutral" size="sm">
                    Verified
                  </Badge>
                </div>
              </Card>
            );
          })}
        </div>
      ) : (
        <EmptyState
          icon={<Sparkles className="w-8 h-8 text-slate-400" />}
          title="No Skills Found"
          description={
            searchQuery
              ? `No skills match your search for "${searchQuery}".`
              : "You haven't registered any skills yet. Add your proficiencies to unlock gap analysis and tailored opportunity matches."
          }
          actionLabel="Add Skill Now"
          onAction={handleOpenAddModal}
        />
      )}

      {/* Add / Edit Skill Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingSkill ? `Edit Level for ${editingSkill.name}` : 'Add New Competency'}
        subtitle="Specify verified mastery level from 1 (Novice) to 5 (Industry Benchmark Expert)"
        footer={
          <>
            <Button variant="outline" size="sm" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" onClick={handleSaveSkill} isLoading={saving}>
              {editingSkill ? 'Save Changes' : 'Add Skill'}
            </Button>
          </>
        }
      >
        <form onSubmit={handleSaveSkill} className="space-y-5">
          {!editingSkill ? (
            <Input
              label="Skill Name"
              placeholder="e.g. Python, Docker, PyTorch, React, SQL"
              value={skillName}
              onChange={(e) => setSkillName(e.target.value)}
              required
            />
          ) : (
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
              <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Skill</span>
              <p className="text-base font-bold text-slate-900 dark:text-slate-100">{skillName}</p>
            </div>
          )}

          {/* Proficiency Level Slider */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-400">
                Proficiency Level (1 - 5)
              </label>
              <span className="text-xs font-bold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/60 px-2 py-0.5 rounded-full border border-brand-200 dark:border-brand-800">
                Level {skillLevel}: {LEVEL_LABELS[skillLevel]?.title}
              </span>
            </div>

            <input
              type="range"
              min="1"
              max="5"
              step="1"
              value={skillLevel}
              onChange={(e) => setSkillLevel(Number(e.target.value))}
              className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-brand-600"
            />

            <div className="flex justify-between text-[11px] text-slate-400 mt-2 px-1">
              <span>1 - Novice</span>
              <span>2 - Basic</span>
              <span>3 - Intermediate</span>
              <span>4 - Advanced</span>
              <span>5 - Expert</span>
            </div>

            <p className="mt-3 text-xs text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-800/40 p-3 rounded-xl border border-slate-200/60 dark:border-slate-700/60">
              {LEVEL_LABELS[skillLevel]?.desc}
            </p>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={Boolean(skillToDelete)}
        onClose={() => setSkillToDelete(null)}
        onConfirm={handleDeleteConfirm}
        title={`Remove ${skillToDelete?.name}?`}
        message="Removing this skill will recalibrate your career readiness score and adjust recommended opportunity ranks."
        confirmLabel="Remove Skill"
        isLoading={deleting}
      />
    </div>
  );
};

export default Skills;
