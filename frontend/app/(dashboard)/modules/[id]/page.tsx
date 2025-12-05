"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import apiClient from '@/lib/api';
import { ModuleStats, CategoryBreakdown } from '@/lib/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function ModuleDashboardPage() {
  const params = useParams();
  const router = useRouter();
  const moduleId = params.id as string;
  const [stats, setStats] = useState<ModuleStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (moduleId) {
      fetchModuleStats();
    }
  }, [moduleId]);

  const fetchModuleStats = async () => {
    try {
      const response = await apiClient.instance.get(`/dashboard/modules/${moduleId}/`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch module stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  if (!stats) {
    return (
      <div className="p-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Module not found</h1>
          <button
            onClick={() => router.back()}
            className="text-blue-600 hover:underline"
          >
            Go back
          </button>
        </div>
      </div>
    );
  }

  const statusData = [
    { name: 'Verified', value: stats.verified_count, color: COLORS[1] },
    { name: 'Submitted', value: stats.submitted_count, color: COLORS[2] },
    { name: 'In Progress', value: stats.in_progress_count, color: COLORS[0] },
    { name: 'Not Started', value: stats.not_started_count, color: COLORS[3] },
  ].filter(item => item.value > 0);

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{stats.module_display_name}</h1>
        <p className="text-gray-600 mt-2">Module Code: {stats.module_code}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader>
            <CardTitle>Overall Completion</CardTitle>
            <CardDescription>All items</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {stats.overall_completion_percent}%
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Total Assignments</CardTitle>
            <CardDescription>Active assignments</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {stats.total_assignments}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Total Items</CardTitle>
            <CardDescription>All items in module</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {stats.total_items}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Templates</CardTitle>
            <CardDescription>Active templates</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {stats.templates_count}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Status Distribution</CardTitle>
            <CardDescription>Items by status</CardDescription>
          </CardHeader>
          <CardContent>
            {statusData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={statusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-gray-500 py-8">No data available</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Item Counts</CardTitle>
            <CardDescription>Breakdown by status</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="font-medium">Verified</span>
                <span className="text-2xl font-bold text-green-600">{stats.verified_count}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                <span className="font-medium">Submitted</span>
                <span className="text-2xl font-bold text-yellow-600">{stats.submitted_count}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <span className="font-medium">In Progress</span>
                <span className="text-2xl font-bold text-blue-600">{stats.in_progress_count}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="font-medium">Not Started</span>
                <span className="text-2xl font-bold text-gray-600">{stats.not_started_count}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {stats.category_breakdown && stats.category_breakdown.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Category Breakdown</CardTitle>
            <CardDescription>Completion by category</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={stats.category_breakdown}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="section_code" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="completion_percent" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {stats.category_breakdown.map((category) => (
                <div
                  key={category.section_code}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div>
                    <div className="font-medium">{category.section_code} - {category.section_title}</div>
                    <div className="text-sm text-gray-600">
                      {category.verified_count} verified / {category.total_items} total
                    </div>
                  </div>
                  <div className="text-lg font-bold">{category.completion_percent}%</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
