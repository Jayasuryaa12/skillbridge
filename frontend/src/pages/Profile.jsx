import React, { useState, useEffect } from 'react';
import {
  User,
  Settings,
  Mail,
  GraduationCap,
  Building,
  Calendar,
  Save,
  Sun,
  Moon,
  Server,
  ShieldCheck,
  CheckCircle2,
  ExternalLink
} from 'lucide-react';
import { useStudent } from '../context/StudentContext';
import { useTheme } from '../context/ThemeContext';
import { useToast } from '../context/ToastContext';
import { updateStudent, SKILL_SERVICE_URL, OPPORTUNITY_SERVICE_URL } from '../api/client';
import Card, { CardHeader, CardContent, CardFooter } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';
import Avatar from '../components/ui/Avatar';
import Badge from '../components/ui/Badge';

export const Profile = () => {
  const { currentStudentId, currentStudent, refreshCurrentStudent } = useStudent();
  const { theme, setTheme } = useTheme();
  const { showToast } = useToast();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    college: '',
    department: '',
    year: 1,
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (currentStudent) {
      setFormData({
        name: currentStudent.name || '',
        email: currentStudent.email || '',
        college: currentStudent.college || '',
        department: currentStudent.department || '',
        year: currentStudent.year || 1,
      });
    }
  }, [currentStudent]);

  const handleUpdate = async (e) => {
    e.preventDefault();
    if (!currentStudentId) return;

    try {
      setSaving(true);
      await updateStudent(currentStudentId, {
        name: formData.name,
        college: formData.college,
        department: formData.department,
        year: Number(formData.year),
      });
      showToast({
        type: 'success',
        title: 'Profile Updated',
        message: 'Your student profile information has been synchronized.',
      });
      await refreshCurrentStudent();
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
          Profile & System Settings
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Manage academic identity, display preferences, and backend microservice connections.
        </p>
      </div>

      {/* Profile Overview Card */}
      <Card className="p-6">
        <div className="flex flex-col sm:flex-row sm:items-center gap-5">
          <Avatar name={formData.name || 'Student'} size="xl" status="online" />
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
                {formData.name || 'Active Student'}
              </h2>
              <Badge variant="brand" size="sm">
                Year {formData.year} Scholar
              </Badge>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
              <Mail className="w-3.5 h-3.5" />
              <span>{formData.email}</span>
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
              <Building className="w-3.5 h-3.5" />
              <span>{formData.department} • {formData.college}</span>
            </p>
          </div>
        </div>
      </Card>

      {/* Edit Information Form */}
      <Card>
        <CardHeader
          title="Academic Identity"
          subtitle="Update your university enrollment and program details"
        />
        <form onSubmit={handleUpdate}>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Full Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
              <Input
                label="Email (Unique ID)"
                value={formData.email}
                disabled
                helperText="Email identifier is bound to the MongoDB document."
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="College / Institute"
                value={formData.college}
                onChange={(e) => setFormData({ ...formData, college: e.target.value })}
                required
              />
              <Input
                label="Department"
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                required
              />
            </div>

            <div className="max-w-xs">
              <Select
                label="Year of Study"
                value={formData.year}
                onChange={(e) => setFormData({ ...formData, year: e.target.value })}
                options={[
                  { value: 1, label: '1st Year (Freshman)' },
                  { value: 2, label: '2nd Year (Sophomore)' },
                  { value: 3, label: '3rd Year (Junior)' },
                  { value: 4, label: '4th Year (Senior)' },
                ]}
              />
            </div>
          </CardContent>

          <CardFooter>
            <Button
              type="submit"
              variant="primary"
              size="sm"
              leftIcon={<Save className="w-4 h-4" />}
              isLoading={saving}
            >
              Save Profile Changes
            </Button>
          </CardFooter>
        </form>
      </Card>

      {/* Theme & Display Preferences */}
      <Card>
        <CardHeader
          title="Display Theme Preferences"
          subtitle="Choose between light mode and dark obsidian mode"
        />
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <button
              type="button"
              onClick={() => setTheme('light')}
              className={`p-4 rounded-xl border flex items-center gap-3 transition-all ${
                theme === 'light'
                  ? 'border-brand-500 bg-brand-50/50 dark:bg-brand-950/40 ring-2 ring-brand-500/20'
                  : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50'
              }`}
            >
              <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-600 flex items-center justify-center shrink-0">
                <Sun className="w-5 h-5" />
              </div>
              <div className="text-left">
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">Light Mode</p>
                <p className="text-xs text-slate-500">Crisp white surfaces with refined slate accents</p>
              </div>
            </button>

            <button
              type="button"
              onClick={() => setTheme('dark')}
              className={`p-4 rounded-xl border flex items-center gap-3 transition-all ${
                theme === 'dark'
                  ? 'border-brand-500 bg-brand-50/50 dark:bg-brand-950/40 ring-2 ring-brand-500/20'
                  : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50'
              }`}
            >
              <div className="w-10 h-10 rounded-xl bg-slate-800 text-indigo-400 flex items-center justify-center shrink-0">
                <Moon className="w-5 h-5" />
              </div>
              <div className="text-left">
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">Dark Mode</p>
                <p className="text-xs text-slate-500">Deep obsidian background with glowing borders</p>
              </div>
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Backend Microservices Architecture Info */}
      <Card>
        <CardHeader
          title="Decoupled Microservice Endpoints"
          subtitle="SkillBridge runs independent HTTP microservices across two ports and discrete MongoDB databases"
        />
        <CardContent className="space-y-3">
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Server className="w-4 h-4 text-brand-600 shrink-0" />
              <div>
                <span className="text-xs font-bold text-slate-900 dark:text-slate-100 block">
                  Skill Service
                </span>
                <span className="text-[11px] font-mono text-slate-500">
                  {SKILL_SERVICE_URL} (Port 5001, Database: skill_db)
                </span>
              </div>
            </div>
            <Badge variant="matched" size="sm">
              Primary Authority
            </Badge>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Server className="w-4 h-4 text-sky-600 shrink-0" />
              <div>
                <span className="text-xs font-bold text-slate-900 dark:text-slate-100 block">
                  Opportunity Service
                </span>
                <span className="text-[11px] font-mono text-slate-500">
                  {OPPORTUNITY_SERVICE_URL} (Port 5002, Database: opportunity_db)
                </span>
              </div>
            </div>
            <Badge variant="brand" size="sm">
              Discovery Engine
            </Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Profile;
