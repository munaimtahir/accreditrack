"use client";

import { ChangeEvent, useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import apiClient from '@/lib/api';
import { ModuleStats, CategoryBreakdown, ProformaTemplate, TemplateStats } from '@/lib/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function ModuleDashboardPage() {
  const params = useParams();
  const router = useRouter();
  const moduleId = params.id as string;
  const [stats, setStats] = useState<ModuleStats | null>(null);
  const [templates, setTemplates] = useState<ProformaTemplate[]>([]);
  const [templateStats, setTemplateStats] = useState<TemplateStats | null>(null);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (moduleId) {
      fetchModuleStats();
      fetchTemplates();
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

  const fetchTemplates = async () => {
    try {
      const response = await apiClient.instance.get('/proformas/templates/', {
        params: { module: moduleId }
      });
      const templatesData = response.data.results || response.data;
      setTemplates(templatesData);
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    }
  };

  const fetchTemplateStats = async (templateId: string) => {
    try {
      const response = await apiClient.instance.get('/dashboard/template-stats/', {
        params: { template_id: templateId }
      });
      setTemplateStats(response.data);
    } catch (error) {
      console.error('Failed to fetch template stats:', error);
    }
  };

  useEffect(() => {
    if (templates.length === 0) {
      setSelectedTemplateId(null);
      setTemplateStats(null);
      return;
    }
    
    setSelectedTemplateId((current) => current ?? templates[0].id);
  }, [templates]);

  useEffect(() => {
    if (selectedTemplateId) {
      fetchTemplateStats(selectedTemplateId);
    } else {
      setTemplateStats(null);
    }
  }, [selectedTemplateId]);

  const handleTemplateChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const value = event.target.value;
    setSelectedTemplateId(value || null);
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
    { name: 'Verified', value: stats.verified_count || 0, color: COLORS[1] },
    { name: 'Submitted', value: stats.submitted_count || 0, color: COLORS[2] },
    { name: 'In Progress', value: stats.in_progress_count || 0, color: COLORS[0] },
    { name: 'Not Started', value: stats.not_started_count || 0, color: COLORS[3] },
    { name: 'Rejected', value: stats.rejected_count || 0, color: COLORS[4] },
  ].filter(item => item.value > 0);

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{stats.module_display_name}</h1>
          <p className="text-gray-600 mt-2">Module Code: {stats.module_code}</p>
        </div>
        {templates.length > 0 && (
          <Button asChild>
            <Link href={`/modules/${moduleId}/template`}>
              View Checklist Template
            </Link>
          </Button>
        )}
      </div>

      {templates.length > 0 && (
        <div className="space-y-4">
          <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-xl font-semibold">Template Insights</h2>
              <p className="text-sm text-gray-600">Track indicator coverage per template</p>
            </div>
            <div className="flex flex-col gap-1 text-sm text-gray-600">
              <label htmlFor="template-select" className="font-medium text-gray-800">
                Select template
              </label>
              <select
                id="template-select"
                className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                value={selectedTemplateId ?? ''}
                onChange={handleTemplateChange}
              >
                {templates.map((template) => (
                  <option key={template.id} value={template.id}>
                    {template.title}{template.code ? ` (${template.code})` : ''}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {templateStats && (
            <div className="grid gap-4 md:grid-cols-3">
              <Card>
                <CardHeader>
                  <CardTitle>Total Indicators</CardTitle>
                  <CardDescription>{templateStats.template_title}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">
                    {templateStats.total_indicators}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Assigned Indicators</CardTitle>
                  <CardDescription>With at least one assignment</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">
                    {templateStats.assigned_indicators}
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    {templateStats.total_indicators > 0 
                      ? `${Math.round((templateStats.assigned_indicators / templateStats.total_indicators) * 100)}% of total`
                      : '0%'}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Indicators with Evidence</CardTitle>
                  <CardDescription>At least one evidence file</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">
                    {templateStats.indicators_with_evidence}
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    {templateStats.total_indicators > 0 
                      ? `${Math.round((templateStats.indicators_with_evidence / templateStats.total_indicators) * 100)}% of total`
                      : '0%'}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      )}

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
            {templates.length > 0 && (
              <div className="mt-2">
                {templates.map((template) => (
                  <Link
                    key={template.id}
                    href={`/modules/${moduleId}/template`}
                    className="text-sm text-blue-600 hover:underline block"
                  >
                    {template.title}
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {templates.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Checklist Templates</CardTitle>
            <CardDescription>Available templates for this module</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {templates.map((template) => (
                <Card key={template.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="font-semibold text-lg">{template.title}</div>
                        <div className="text-sm text-gray-600 mt-1">
                          {template.authority_name} • Version {template.version}
                        </div>
                        {template.description && (
                          <div className="text-sm text-gray-500 mt-1">{template.description}</div>
                        )}
                        <div className="text-sm text-gray-500 mt-2">
                          {template.sections_count || 0} sections
                        </div>
                      </div>
                      <Button asChild variant="outline">
                        <Link href={`/modules/${moduleId}/template`}>
                          View Checklist
                        </Link>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

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
                <span className="text-2xl font-bold text-yellow-600">{stats.submitted_count || 0}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <span className="font-medium">In Progress</span>
                <span className="text-2xl font-bold text-blue-600">{stats.in_progress_count}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="font-medium">Not Started</span>
                <span className="text-2xl font-bold text-gray-600">{stats.not_started_count}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                <span className="font-medium">Rejected</span>
                <span className="text-2xl font-bold text-red-600">{stats.rejected_count}</span>
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
