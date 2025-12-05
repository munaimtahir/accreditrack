"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import apiClient from '@/lib/api';
import { ProformaTemplate, ProformaSection, ProformaItem, Module } from '@/lib/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function TemplateBrowserPage() {
  const params = useParams();
  const router = useRouter();
  const moduleId = params.id as string;
  const { user, hasRole } = useAuth();
  const [template, setTemplate] = useState<ProformaTemplate | null>(null);
  const [module, setModule] = useState<Module | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedStandard, setSelectedStandard] = useState<string | null>(null);
  const [assignmentDialogOpen, setAssignmentDialogOpen] = useState(false);
  const [assignmentData, setAssignmentData] = useState({
    scope_type: 'SECTION' as 'SECTION' | 'INDICATOR',
    section_id: '',
    proforma_item_id: '',
    instructions: '',
    start_date: '',
    due_date: '',
    department_id: '',
  });

  useEffect(() => {
    if (moduleId) {
      fetchModule();
      fetchTemplate();
    }
  }, [moduleId]);

  const fetchModule = async () => {
    try {
      const response = await apiClient.instance.get(`/modules/${moduleId}/`);
      setModule(response.data);
    } catch (error) {
      console.error('Failed to fetch module:', error);
    }
  };

  const fetchTemplate = async () => {
    try {
      // Try to fetch template by code first, then by module
      let response;
      try {
        response = await apiClient.instance.get('/proformas/templates/', {
          params: { code: 'PHC-MSDS-2018', module: moduleId }
        });
      } catch {
        // Fallback: fetch by module
        response = await apiClient.instance.get('/proformas/templates/', {
          params: { module: moduleId }
        });
      }
      
      const templates = response.data.results || response.data;
      if (templates.length > 0) {
        // Fetch full template details with sections
        const templateResponse = await apiClient.instance.get(`/proformas/templates/${templates[0].id}/`);
        setTemplate(templateResponse.data);
      }
    } catch (error) {
      console.error('Failed to fetch template:', error);
    } finally {
      setLoading(false);
    }
  };

  const canCreateAssignment = (): boolean => {
    if (!user) return false;
    // Check if user has DASHBOARD_ADMIN or CATEGORY_ADMIN role for this module
    // This would need to check user.module_roles - simplified for now
    return user.is_staff || hasRole('SuperAdmin');
  };

  const handleCreateAssignment = async () => {
    if (!template) return;

    try {
      const payload: any = {
        proforma_template_id: template.id,
        scope_type: assignmentData.scope_type,
        instructions: assignmentData.instructions,
        start_date: assignmentData.start_date,
        due_date: assignmentData.due_date,
      };

      if (assignmentData.scope_type === 'SECTION' && assignmentData.section_id) {
        payload.section = assignmentData.section_id;
      } else if (assignmentData.scope_type === 'INDICATOR' && assignmentData.proforma_item_id) {
        payload.proforma_item = assignmentData.proforma_item_id;
      }

      if (assignmentData.department_id) {
        payload.department_id = assignmentData.department_id;
      }

      await apiClient.instance.post('/assignments/', payload);
      setAssignmentDialogOpen(false);
      // Reset form
      setAssignmentData({
        scope_type: 'SECTION',
        section_id: '',
        proforma_item_id: '',
        instructions: '',
        start_date: '',
        due_date: '',
        department_id: '',
      });
      alert('Assignment created successfully!');
    } catch (error: any) {
      console.error('Failed to create assignment:', error);
      alert(error.response?.data?.detail || 'Failed to create assignment');
    }
  };

  if (loading) {
    return <div className="p-8">Loading template...</div>;
  }

  if (!template) {
    return (
      <div className="p-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Template not found</h1>
          <p className="text-gray-600 mb-4">The PHC MSDS checklist template has not been seeded yet.</p>
          <Button onClick={() => router.back()}>Go back</Button>
        </div>
      </div>
    );
  }

  const categories = template.sections || [];

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Button variant="ghost" onClick={() => router.back()} className="mb-4">
            ← Back to Dashboard
          </Button>
          <h1 className="text-3xl font-bold">{template.title}</h1>
          <p className="text-gray-600 mt-2">
            {module?.display_name} • Version {template.version} • Authority: {template.authority_name}
          </p>
          {template.description && (
            <p className="text-gray-500 mt-1">{template.description}</p>
          )}
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Checklist Structure</CardTitle>
          <CardDescription>
            {categories.length} categories, {template.sections_count || 0} total sections
          </CardDescription>
        </CardHeader>
      </Card>

      <div className="space-y-4">
        {categories.map((category: ProformaSection) => (
          <Card key={category.id} className="overflow-hidden">
            <CardHeader
              className="cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => setSelectedCategory(selectedCategory === category.code ? null : category.code)}
            >
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">
                    {category.code} - {category.title}
                  </CardTitle>
                  <CardDescription>
                    {category.children?.length || 0} standards, {category.items_count || 0} indicators
                  </CardDescription>
                </div>
                <div className="text-2xl">{selectedCategory === category.code ? '−' : '+'}</div>
              </div>
            </CardHeader>

            {selectedCategory === category.code && (
              <CardContent className="space-y-4 pt-0">
                {category.children?.map((standard: ProformaSection) => (
                  <Card key={standard.id} className="border-l-4 border-l-blue-500">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <CardTitle className="text-md">
                            {standard.code} - {standard.title}
                          </CardTitle>
                          <CardDescription>
                            {standard.items_count || 0} indicators
                          </CardDescription>
                        </div>
                        {canCreateAssignment() && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setAssignmentData(prev => ({
                                ...prev,
                                scope_type: 'SECTION',
                                section_id: standard.id,
                              }));
                              setAssignmentDialogOpen(true);
                            }}
                          >
                            Assign Standard
                          </Button>
                        )}
                      </div>
                    </CardHeader>

                    <CardContent className="pt-0">
                      <div
                        className="cursor-pointer text-sm text-blue-600 hover:underline mb-2"
                        onClick={() => setSelectedStandard(selectedStandard === standard.code ? null : standard.code)}
                      >
                        {selectedStandard === standard.code ? 'Hide' : 'Show'} indicators ({standard.items_count || 0})
                      </div>

                      {selectedStandard === standard.code && standard.items && (
                        <div className="space-y-3 mt-3">
                          {standard.items.map((indicator: ProformaItem) => (
                            <Card key={indicator.id} className="bg-gray-50">
                              <CardContent className="p-4">
                                <div className="flex items-start justify-between">
                                  <div className="flex-1">
                                    <div className="font-mono text-sm font-medium text-gray-700 mb-1">
                                      {indicator.code}
                                    </div>
                                    <div className="text-sm text-gray-800 mb-2">
                                      {indicator.requirement_text}
                                    </div>
                                    <div className="flex items-center gap-4 text-xs text-gray-500">
                                      <span>Max Score: {indicator.max_score || 10}</span>
                                      <span>Weightage: {indicator.weightage_percent || 100}%</span>
                                      {indicator.is_licensing_critical && (
                                        <span className="text-red-600 font-medium">Licensing Critical</span>
                                      )}
                                    </div>
                                    {indicator.implementation_criteria && (
                                      <div className="text-xs text-gray-600 mt-2 italic">
                                        {indicator.implementation_criteria}
                                      </div>
                                    )}
                                  </div>
                                  {canCreateAssignment() && (
                                    <Button
                                      size="sm"
                                      variant="outline"
                                      className="ml-4"
                                      onClick={() => {
                                        setAssignmentData(prev => ({
                                          ...prev,
                                          scope_type: 'INDICATOR',
                                          proforma_item_id: indicator.id,
                                          section_id: standard.id,
                                        }));
                                        setAssignmentDialogOpen(true);
                                      }}
                                    >
                                      Assign
                                    </Button>
                                  )}
                                </div>
                              </CardContent>
                            </Card>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </CardContent>
            )}
          </Card>
        ))}
      </div>

      {/* Assignment Creation Dialog */}
      <Dialog open={assignmentDialogOpen} onOpenChange={setAssignmentDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create Assignment</DialogTitle>
            <DialogDescription>
              Create a new assignment for {assignmentData.scope_type === 'SECTION' ? 'this standard' : 'this indicator'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="instructions">Instructions</Label>
              <textarea
                id="instructions"
                className="w-full mt-1 p-2 border rounded-md"
                rows={3}
                value={assignmentData.instructions}
                onChange={(e) => setAssignmentData(prev => ({ ...prev, instructions: e.target.value }))}
                placeholder="Enter assignment instructions..."
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="start_date">Start Date</Label>
                <Input
                  id="start_date"
                  type="date"
                  value={assignmentData.start_date}
                  onChange={(e) => setAssignmentData(prev => ({ ...prev, start_date: e.target.value }))}
                />
              </div>
              <div>
                <Label htmlFor="due_date">Due Date</Label>
                <Input
                  id="due_date"
                  type="date"
                  value={assignmentData.due_date}
                  onChange={(e) => setAssignmentData(prev => ({ ...prev, due_date: e.target.value }))}
                />
              </div>
            </div>
            <div>
              <Label htmlFor="department_id">Department ID (optional)</Label>
              <Input
                id="department_id"
                type="text"
                value={assignmentData.department_id}
                onChange={(e) => setAssignmentData(prev => ({ ...prev, department_id: e.target.value }))}
                placeholder="Enter department UUID"
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setAssignmentDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreateAssignment}>
                Create Assignment
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
