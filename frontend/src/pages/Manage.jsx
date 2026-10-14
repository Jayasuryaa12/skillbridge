import React, { useState, useEffect } from 'react';
import {
  SlidersHorizontal,
  Users,
  Compass,
  Briefcase,
  Plus,
  Trash2,
  Edit2,
  Search,
  ExternalLink,
  ShieldCheck
} from 'lucide-react';
import { useStudent } from '../context/StudentContext';
import { useToast } from '../context/ToastContext';
import {
  getStudents,
  createStudent,
  deleteStudent,
  getCareers,
  createCareer,
  deleteCareer,
  getOpportunities,
  createOpportunity,
  deleteOpportunity
} from '../api/client';
import Card, { CardHeader, CardContent } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';
import Modal from '../components/ui/Modal';
import Tabs from '../components/ui/Tabs';
import Table, { TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/Table';
import ConfirmDialog from '../components/ui/ConfirmDialog';
import Badge from '../components/ui/Badge';
import Skeleton from '../components/ui/Skeleton';

export const Manage = () => {
  const { refreshStudentsList } = useStudent();
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState('students');

  // Lists state
  const [students, setStudents] = useState([]);
  const [careers, setCareers] = useState([]);
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);

  // Add Modals
  const [isAddStudentOpen, setIsAddStudentOpen] = useState(false);
  const [isAddCareerOpen, setIsAddCareerOpen] = useState(false);
  const [isAddOppOpen, setIsAddOppOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  // Form States
  const [studentForm, setStudentForm] = useState({
    name: '',
    email: '',
    college: '',
    department: 'Computer Science',
    year: 3,
  });

  const [careerForm, setCareerForm] = useState({
    title: '',
    description: '',
    category: 'Engineering',
    required_skills: 'Python:3, Docker:3, SQL:3',
  });

  const [oppForm, setOppForm] = useState({
    title: '',
    company: '',
    type: 'internship',
    location: 'Remote',
    remote: true,
    stipend: '$35/hr',
    description: '',
    required_skills: 'Python, Docker',
    link: 'https://example.com/apply',
  });

  // Delete Confirm
  const [deleteTarget, setDeleteTarget] = useState(null); // { type, id, name }
  const [deleting, setDeleting] = useState(false);

  const fetchTabData = async () => {
    try {
      setLoading(true);
      if (activeTab === 'students') {
        const res = await getStudents({ limit: 100 });
        const list = res.data || res.students || [];
        setStudents(list.map((s) => ({ ...s, id: s.id || s._id })));
      } else if (activeTab === 'careers') {
        const res = await getCareers();
        const list = res.data || res.careers || [];
        setCareers(list.map((c) => ({ ...c, id: c.id || c._id })));
      } else if (activeTab === 'opportunities') {
        const res = await getOpportunities({ limit: 100 });
        const list = res.data || res.opportunities || [];
        setOpportunities(list.map((o) => ({ ...o, id: o.id || o._id })));
      }
    } catch (err) {
      console.error('Failed to load manage tab data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTabData();
  }, [activeTab]);

  // Submit Student
  const handleCreateStudent = async (e) => {
    e.preventDefault();
    try {
      setSaving(true);
      await createStudent({
        ...studentForm,
        year: Number(studentForm.year),
      });
      showToast({ type: 'success', title: 'Student Registered', message: `${studentForm.name} added to Skill Service database.` });
      setIsAddStudentOpen(false);
      setStudentForm({ name: '', email: '', college: '', department: 'Computer Science', year: 3 });
      await fetchTabData();
      await refreshStudentsList();
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  // Submit Career
  const handleCreateCareer = async (e) => {
    e.preventDefault();
    try {
      setSaving(true);
      const parsedSkills = careerForm.required_skills.split(',').map((item) => {
        const [name, lvl] = item.trim().split(':');
        return {
          name: name.trim(),
          required_level: Number(lvl || 3),
          importance: 4,
          prerequisites: [],
          category: careerForm.category,
        };
      });

      await createCareer({
        title: careerForm.title,
        description: careerForm.description,
        category: careerForm.category,
        required_skills: parsedSkills,
      });

      showToast({ type: 'success', title: 'Career Track Created', message: `${careerForm.title} successfully persisted.` });
      setIsAddCareerOpen(false);
      setCareerForm({ title: '', description: '', category: 'Engineering', required_skills: 'Python:3, Docker:3' });
      await fetchTabData();
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  // Submit Opportunity
  const handleCreateOpportunity = async (e) => {
    e.preventDefault();
    try {
      setSaving(true);
      const parsedSkills = oppForm.required_skills.split(',').map((s) => ({
        name: s.trim(),
        required_level: 3,
      }));

      await createOpportunity({
        title: oppForm.title,
        company: oppForm.company,
        type: oppForm.type,
        location: oppForm.location,
        remote: oppForm.remote,
        stipend: oppForm.stipend,
        description: oppForm.description,
        required_skills: parsedSkills,
        link: oppForm.link,
      });

      showToast({ type: 'success', title: 'Opportunity Published', message: `${oppForm.title} added to Opportunity Service.` });
      setIsAddOppOpen(false);
      await fetchTabData();
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  // Delete Handler
  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    try {
      setDeleting(true);
      if (deleteTarget.type === 'student') {
        await deleteStudent(deleteTarget.id);
        await refreshStudentsList();
      } else if (deleteTarget.type === 'career') {
        await deleteCareer(deleteTarget.id);
      } else if (deleteTarget.type === 'opportunity') {
        await deleteOpportunity(deleteTarget.id);
      }
      showToast({ type: 'success', title: 'Deleted', message: `${deleteTarget.name} has been removed.` });
      setDeleteTarget(null);
      await fetchTabData();
    } catch (err) {
      console.error(err);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
            System Administration & Records
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Manage student profiles, career tracks, and job opportunities across both microservices.
          </p>
        </div>

        {/* Add Actions Button depending on active tab */}
        {activeTab === 'students' && (
          <Button
            variant="primary"
            leftIcon={<Plus className="w-4 h-4" />}
            onClick={() => setIsAddStudentOpen(true)}
          >
            Register Student
          </Button>
        )}
        {activeTab === 'careers' && (
          <Button
            variant="primary"
            leftIcon={<Plus className="w-4 h-4" />}
            onClick={() => setIsAddCareerOpen(true)}
          >
            Create Career Goal
          </Button>
        )}
        {activeTab === 'opportunities' && (
          <Button
            variant="primary"
            leftIcon={<Plus className="w-4 h-4" />}
            onClick={() => setIsAddOppOpen(true)}
          >
            Post Opportunity
          </Button>
        )}
      </div>

      {/* Tabs */}
      <Tabs
        tabs={[
          { id: 'students', label: 'Students Directory', icon: <Users className="w-4 h-4" />, badge: students.length },
          { id: 'careers', label: 'Career Tracks', icon: <Compass className="w-4 h-4" />, badge: careers.length },
          { id: 'opportunities', label: 'Opportunities Catalog', icon: <Briefcase className="w-4 h-4" />, badge: opportunities.length },
        ]}
        activeTab={activeTab}
        onChange={setActiveTab}
      />

      {/* Content Table by Tab */}
      <Card>
        {loading ? (
          <div className="p-6 space-y-4">
            <Skeleton height="36px" />
            <Skeleton height="36px" />
            <Skeleton height="36px" />
          </div>
        ) : (
          <>
            {/* STUDENTS TAB */}
            {activeTab === 'students' && (
              <Table>
                <TableHeader>
                  <TableRow hover={false}>
                    <TableHead>Student Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Department / College</TableHead>
                    <TableHead>Year</TableHead>
                    <TableHead>Skills Count</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {students.map((s) => (
                    <TableRow key={s.id}>
                      <TableCell className="font-semibold text-slate-900 dark:text-slate-100">
                        {s.name}
                      </TableCell>
                      <TableCell>{s.email}</TableCell>
                      <TableCell>
                        {s.department} • <span className="text-slate-400">{s.college}</span>
                      </TableCell>
                      <TableCell>Year {s.year}</TableCell>
                      <TableCell>
                        <Badge variant="brand" size="sm">
                          {s.skills?.length || 0} skills
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="dangerOutline"
                          size="iconSm"
                          onClick={() => setDeleteTarget({ type: 'student', id: s.id, name: s.name })}
                          title="Delete student"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}

            {/* CAREERS TAB */}
            {activeTab === 'careers' && (
              <Table>
                <TableHeader>
                  <TableRow hover={false}>
                    <TableHead>Career Title</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Required Competencies</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {careers.map((c) => (
                    <TableRow key={c.id}>
                      <TableCell className="font-semibold text-slate-900 dark:text-slate-100">
                        {c.title}
                      </TableCell>
                      <TableCell>
                        <Badge variant="neutral" size="sm">
                          {c.category}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1 max-w-md">
                          {(c.required_skills || []).slice(0, 4).map((sk, idx) => (
                            <span key={idx} className="text-[11px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                              {sk.name} (L{sk.required_level})
                            </span>
                          ))}
                          {(c.required_skills?.length || 0) > 4 && (
                            <span className="text-[11px] text-slate-400">+{c.required_skills.length - 4} more</span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="dangerOutline"
                          size="iconSm"
                          onClick={() => setDeleteTarget({ type: 'career', id: c.id, name: c.title })}
                          title="Delete career track"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}

            {/* OPPORTUNITIES TAB */}
            {activeTab === 'opportunities' && (
              <Table>
                <TableHeader>
                  <TableRow hover={false}>
                    <TableHead>Role Title</TableHead>
                    <TableHead>Company</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Stipend</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {opportunities.map((opp) => (
                    <TableRow key={opp.id}>
                      <TableCell className="font-semibold text-slate-900 dark:text-slate-100">
                        {opp.title}
                      </TableCell>
                      <TableCell>{opp.company}</TableCell>
                      <TableCell>
                        <Badge variant="brand" size="sm">
                          {opp.type}
                        </Badge>
                      </TableCell>
                      <TableCell>{opp.remote ? 'Remote' : opp.location}</TableCell>
                      <TableCell>{opp.stipend || 'Competitive'}</TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="dangerOutline"
                          size="iconSm"
                          onClick={() => setDeleteTarget({ type: 'opportunity', id: opp.id, name: opp.title })}
                          title="Delete opportunity"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </>
        )}
      </Card>

      {/* Modal: Add Student */}
      <Modal
        isOpen={isAddStudentOpen}
        onClose={() => setIsAddStudentOpen(false)}
        title="Register New Student"
        subtitle="Saved to skill_db on Port 5001"
        footer={
          <>
            <Button variant="outline" size="sm" onClick={() => setIsAddStudentOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" onClick={handleCreateStudent} isLoading={saving}>
              Register Student
            </Button>
          </>
        }
      >
        <form onSubmit={handleCreateStudent} className="space-y-4">
          <Input
            label="Full Name"
            placeholder="e.g. Maya Lin"
            value={studentForm.name}
            onChange={(e) => setStudentForm({ ...studentForm, name: e.target.value })}
            required
          />
          <Input
            label="Email Address"
            type="email"
            placeholder="e.g. maya@university.edu"
            value={studentForm.email}
            onChange={(e) => setStudentForm({ ...studentForm, email: e.target.value })}
            required
          />
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="College / Institute"
              placeholder="e.g. Stanford University"
              value={studentForm.college}
              onChange={(e) => setStudentForm({ ...studentForm, college: e.target.value })}
              required
            />
            <Select
              label="Year of Study"
              value={studentForm.year}
              onChange={(e) => setStudentForm({ ...studentForm, year: e.target.value })}
              options={[
                { value: 1, label: 'Year 1 (Freshman)' },
                { value: 2, label: 'Year 2 (Sophomore)' },
                { value: 3, label: 'Year 3 (Junior)' },
                { value: 4, label: 'Year 4 (Senior)' },
              ]}
            />
          </div>
          <Input
            label="Department"
            placeholder="e.g. Computer Science & AI"
            value={studentForm.department}
            onChange={(e) => setStudentForm({ ...studentForm, department: e.target.value })}
            required
          />
        </form>
      </Modal>

      {/* Modal: Add Career */}
      <Modal
        isOpen={isAddCareerOpen}
        onClose={() => setIsAddCareerOpen(false)}
        title="Create Career Goal Track"
        subtitle="Define industry requirements and prerequisite competencies"
        footer={
          <>
            <Button variant="outline" size="sm" onClick={() => setIsAddCareerOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" onClick={handleCreateCareer} isLoading={saving}>
              Save Career Track
            </Button>
          </>
        }
      >
        <form onSubmit={handleCreateCareer} className="space-y-4">
          <Input
            label="Role Title"
            placeholder="e.g. Cloud DevOps Architect"
            value={careerForm.title}
            onChange={(e) => setCareerForm({ ...careerForm, title: e.target.value })}
            required
          />
          <Input
            label="Category"
            placeholder="e.g. Cloud & Infrastructure"
            value={careerForm.category}
            onChange={(e) => setCareerForm({ ...careerForm, category: e.target.value })}
            required
          />
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1.5">
              Description
            </label>
            <textarea
              rows={3}
              value={careerForm.description}
              onChange={(e) => setCareerForm({ ...careerForm, description: e.target.value })}
              className="w-full rounded-xl bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 text-sm p-3 text-slate-900 dark:text-slate-100 outline-none"
              placeholder="Summary of responsibilities and target expectations..."
              required
            />
          </div>
          <Input
            label="Required Skills (Format: Skill:Level)"
            placeholder="e.g. Kubernetes:4, Terraform:3, Python:3, AWS:4"
            value={careerForm.required_skills}
            onChange={(e) => setCareerForm({ ...careerForm, required_skills: e.target.value })}
            helperText="Separate competencies with commas and specify required target mastery level (1-5)"
            required
          />
        </form>
      </Modal>

      {/* Modal: Add Opportunity */}
      <Modal
        isOpen={isAddOppOpen}
        onClose={() => setIsAddOppOpen(false)}
        title="Publish Opportunity"
        subtitle="Saved to opportunity_db on Port 5002"
        footer={
          <>
            <Button variant="outline" size="sm" onClick={() => setIsAddOppOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" onClick={handleCreateOpportunity} isLoading={saving}>
              Publish Opportunity
            </Button>
          </>
        }
      >
        <form onSubmit={handleCreateOpportunity} className="space-y-4">
          <Input
            label="Opportunity Title"
            placeholder="e.g. Machine Learning Research Intern"
            value={oppForm.title}
            onChange={(e) => setOppForm({ ...oppForm, title: e.target.value })}
            required
          />
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Company / Lab"
              placeholder="e.g. OpenAI, DeepMind, Stripe"
              value={oppForm.company}
              onChange={(e) => setOppForm({ ...oppForm, company: e.target.value })}
              required
            />
            <Select
              label="Type"
              value={oppForm.type}
              onChange={(e) => setOppForm({ ...oppForm, type: e.target.value })}
              options={[
                { value: 'internship', label: 'Internship' },
                { value: 'full_time', label: 'Full-Time' },
                { value: 'hackathon', label: 'Hackathon' },
                { value: 'open_source', label: 'Open Source' },
                { value: 'research', label: 'Research' },
              ]}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Location"
              placeholder="e.g. San Francisco, CA"
              value={oppForm.location}
              onChange={(e) => setOppForm({ ...oppForm, location: e.target.value })}
              required
            />
            <Input
              label="Stipend / Comp"
              placeholder="e.g. $45/hr"
              value={oppForm.stipend}
              onChange={(e) => setOppForm({ ...oppForm, stipend: e.target.value })}
            />
          </div>
          <Input
            label="Required Competencies (Comma-separated)"
            placeholder="e.g. Python, PyTorch, Docker"
            value={oppForm.required_skills}
            onChange={(e) => setOppForm({ ...oppForm, required_skills: e.target.value })}
            required
          />
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1.5">
              Description
            </label>
            <textarea
              rows={3}
              value={oppForm.description}
              onChange={(e) => setOppForm({ ...oppForm, description: e.target.value })}
              className="w-full rounded-xl bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 text-sm p-3 text-slate-900 dark:text-slate-100 outline-none"
              placeholder="Role description, project scope, requirements..."
              required
            />
          </div>
        </form>
      </Modal>

      {/* Delete Confirm Dialog */}
      <ConfirmDialog
        isOpen={Boolean(deleteTarget)}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDeleteConfirm}
        title={`Delete ${deleteTarget?.name}?`}
        message="This action permanently removes the record from MongoDB. Dependent gap analyses will be automatically updated."
        confirmLabel="Confirm Deletion"
        isLoading={deleting}
      />
    </div>
  );
};

export default Manage;
