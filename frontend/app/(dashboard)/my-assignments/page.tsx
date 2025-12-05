"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import apiClient from '@/lib/api';
import { ModuleAssignment } from '@/lib/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function MyAssignmentsPage() {
  const router = useRouter();
  const [assignments, setAssignments] = useState<ModuleAssignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [moduleFilter, setModuleFilter] = useState<string>('');

  useEffect(() => {
    fetchAssignments();
  }, [moduleFilter]);

  const fetchAssignments = async () => {
    try {
      const params = moduleFilter ? { module: moduleFilter } : {};
      const response = await apiClient.instance.get('/dashboard/user-assignments/', { params });
      setAssignments(response.data);
    } catch (error) {
      console.error('Failed to fetch assignments:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Completed':
        return 'bg-green-100 text-green-800';
      case 'InProgress':
        return 'bg-blue-100 text-blue-800';
      case 'NotStarted':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">My Assignments</h1>
        <p className="text-gray-600 mt-2">View and manage your assigned tasks</p>
      </div>

      <div className="flex gap-4 items-center">
        <label className="text-sm font-medium">Filter by Module:</label>
        <input
          type="text"
          placeholder="Module code (optional)"
          value={moduleFilter}
          onChange={(e) => setModuleFilter(e.target.value)}
          className="px-3 py-2 border rounded-md"
        />
        {moduleFilter && (
          <button
            onClick={() => setModuleFilter('')}
            className="text-sm text-blue-600 hover:underline"
          >
            Clear filter
          </button>
        )}
      </div>

      {assignments.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center text-gray-500">
            No assignments found
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {assignments.map((assignment) => (
            <Card key={assignment.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle>{assignment.proforma_template_title}</CardTitle>
                    <CardDescription>
                      {assignment.module_code && (
                        <span className="mr-2">Module: {assignment.module_code}</span>
                      )}
                      Scope: {assignment.scope_type}
                      {assignment.section_code && ` - Section: ${assignment.section_code}`}
                      {assignment.proforma_item_code && ` - Item: ${assignment.proforma_item_code}`}
                    </CardDescription>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(assignment.status)}`}>
                    {assignment.status}
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <div className="text-sm text-gray-600">Completion</div>
                    <div className="text-2xl font-bold">{assignment.completion_percent}%</div>
                    <div className="text-sm text-gray-500">
                      {assignment.verified_items} / {assignment.total_items} items verified
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Dates</div>
                    <div className="text-sm">
                      <div>Start: {formatDate(assignment.start_date)}</div>
                      <div>Due: {formatDate(assignment.due_date)}</div>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Instructions</div>
                    <div className="text-sm text-gray-700">
                      {assignment.instructions || 'No instructions provided'}
                    </div>
                  </div>
                </div>
                <div className="mt-4">
                  <button
                    onClick={() => router.push(`/assignments/${assignment.id}`)}
                    className="text-blue-600 hover:underline text-sm font-medium"
                  >
                    View Details →
                  </button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
