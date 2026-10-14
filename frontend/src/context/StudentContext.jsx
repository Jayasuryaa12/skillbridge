import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getStudents, getStudent } from '../api/client';

const StudentContext = createContext(null);

export const StudentProvider = ({ children }) => {
  const [students, setStudents] = useState([]);
  const [currentStudentId, setCurrentStudentId] = useState(() => {
    return localStorage.getItem('skillbridge_student_id') || '';
  });
  const [currentStudent, setCurrentStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch list of students
  const fetchStudents = useCallback(async () => {
    try {
      setLoading(true);
      const res = await getStudents({ limit: 50 });
      const rawList = res.data || res.students || [];
      const list = rawList.map((s) => ({
        ...s,
        id: s.id || s._id,
      }));
      setStudents(list);

      // If we don't have a valid active student ID, pick the first one
      if (list.length > 0) {
        const storedId = localStorage.getItem('skillbridge_student_id');
        const exists = list.some((s) => s.id === storedId);
        const selectedId = exists ? storedId : list[0].id;
        setCurrentStudentId(selectedId);
        localStorage.setItem('skillbridge_student_id', selectedId);
      }
      setError(null);
    } catch (err) {
      console.error('Failed to load students list:', err);
      setError('Could not connect to Skill Service. Ensure service is running on port 5001.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch active student details whenever currentStudentId changes
  const fetchCurrentStudent = useCallback(async (id) => {
    if (!id) {
      setCurrentStudent(null);
      return;
    }
    try {
      const res = await getStudent(id);
      const studentData = res.data || res.student || res;
      setCurrentStudent({
        ...studentData,
        id: studentData.id || studentData._id,
      });
    } catch (err) {
      console.error(`Failed to load student ${id}:`, err);
    }
  }, []);

  useEffect(() => {
    fetchStudents();
  }, [fetchStudents]);

  useEffect(() => {
    if (currentStudentId) {
      fetchCurrentStudent(currentStudentId);
      localStorage.setItem('skillbridge_student_id', currentStudentId);
    }
  }, [currentStudentId, fetchCurrentStudent]);

  const selectStudent = (studentId) => {
    setCurrentStudentId(studentId);
    const found = students.find((s) => s.id === studentId);
    if (found) setCurrentStudent(found);
  };

  const refreshCurrentStudent = () => {
    if (currentStudentId) {
      return fetchCurrentStudent(currentStudentId);
    }
  };

  return (
    <StudentContext.Provider
      value={{
        students,
        currentStudentId,
        currentStudent,
        loading,
        error,
        selectStudent,
        refreshCurrentStudent,
        refreshStudentsList: fetchStudents,
      }}
    >
      {children}
    </StudentContext.Provider>
  );
};

export const useStudent = () => {
  const context = useContext(StudentContext);
  if (!context) {
    throw new Error('useStudent must be used within a StudentProvider');
  }
  return context;
};
