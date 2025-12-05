"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import apiClient from '@/lib/api';
import { Assignment } from '@/lib/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

export default function AssignmentsPage() {
  const { isQAAdmin } = useAuth();
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAssignments();
  }, []);

  const fetchAssignments = async () => {
    try {
      const response = await apiClient.instance.get('/assignments/');
      setAssignments(response.data.results || response.data);
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
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Assignments</h1>
          <p className="text-gray-600 mt-2">View and manage department assignments</p>
        </div>
        {isQAAdmin && (
          <Button asChild>
            <Link href="/assignments/new">Create Assignment</Link>
          </Button>
        )}
      </div>

      <div className="grid gap-4">
        {assignments.map((assignment) => (
          <Link key={assignment.id} href={`/assignments/${assignment.id}`}>
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>{assignment.proforma_template.title}</CardTitle>
                    <CardDescription>
                      {assignment.department.name} - Due: {new Date(assignment.due_date).toLocaleDateString()}
                    </CardDescription>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(assignment.status)}`}
                  >
                    {assignment.status}
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4">
                  <div>
                    <div className="text-sm text-gray-600">Completion</div>
                    <div className="text-2xl font-bold">
                      {assignment.completion_percent}%
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${assignment.completion_percent}%` }}
                      />
                    </div>
                  </div>
                  <div className="text-sm text-gray-600">
                    {assignment.verified_count} / {assignment.items_count} verified
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      {assignments.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No assignments found
        </div>
      )}
    </div>
  );
}
