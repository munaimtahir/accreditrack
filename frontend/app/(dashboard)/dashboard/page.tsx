"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import apiClient from '@/lib/api';
import { DashboardSummary, PendingItem, ModuleStats } from '@/lib/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isQAAdmin } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [pendingItems, setPendingItems] = useState<PendingItem[]>([]);
  const [modules, setModules] = useState<ModuleStats[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [summaryRes, pendingRes] = await Promise.all([
        apiClient.instance.get('/dashboard/summary/'),
        apiClient.instance.get('/dashboard/pending-items/'),
      ]);
      setSummary(summaryRes.data);
      setPendingItems(pendingRes.data);
      
      // Fetch modules if user is super admin
      if (isQAAdmin) {
        try {
          const modulesRes = await apiClient.instance.get('/dashboard/modules/');
          setModules(modulesRes.data);
        } catch (error) {
          console.error('Failed to fetch modules:', error);
        }
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Welcome back, {user?.full_name}
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader>
            <CardTitle>Overall Completion</CardTitle>
            <CardDescription>All assignments</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {summary?.overall_completion_percent || 0}%
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Active Assignments</CardTitle>
            <CardDescription>In progress</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {summary?.assignments.length || 0}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pending Items</CardTitle>
            <CardDescription>Requiring attention</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{pendingItems.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Verified Items</CardTitle>
            <CardDescription>Completed</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {summary?.assignments.reduce((acc, a) => acc + (a.completion_percent * 10), 0) || 0}
            </div>
          </CardContent>
        </Card>
      </div>

      {summary && summary.sections.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Completion by Section</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={summary.sections}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="code" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="completion_percent" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {modules.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Accreditation Modules</CardTitle>
            <CardDescription>Available modules</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {modules.map((module) => (
                <Card
                  key={module.module_id}
                  className="cursor-pointer hover:shadow-lg transition-shadow"
                  onClick={() => router.push(`/modules/${module.module_id}`)}
                >
                  <CardHeader>
                    <CardTitle className="text-lg">{module.module_display_name}</CardTitle>
                    <CardDescription>{module.module_code}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Completion:</span>
                        <span className="text-sm font-bold">{module.overall_completion_percent}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Assignments:</span>
                        <span className="text-sm font-bold">{module.total_assignments}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Items:</span>
                        <span className="text-sm font-bold">{module.total_items}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {pendingItems.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Pending Items</CardTitle>
            <CardDescription>Items requiring attention</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {pendingItems.slice(0, 10).map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div>
                    <div className="font-medium">{item.item_code}</div>
                    <div className="text-sm text-gray-600">
                      {item.department_name} - {item.assignment_title}
                    </div>
                  </div>
                  <div className="text-sm text-gray-500">{item.status}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
