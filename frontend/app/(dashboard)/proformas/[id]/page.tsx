"use client";

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import apiClient from '@/lib/api';
import { ProformaTemplate } from '@/lib/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function ProformaDetailPage() {
  const params = useParams();
  const { isQAAdmin } = useAuth();
  const [template, setTemplate] = useState<ProformaTemplate | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.id) {
      fetchTemplate(params.id as string);
    }
  }, [params.id]);

  const fetchTemplate = async (id: string) => {
    try {
      const response = await apiClient.instance.get(`/proformas/templates/${id}/`);
      setTemplate(response.data);
    } catch (error) {
      console.error('Failed to fetch template:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  if (!template) {
    return <div className="p-8">Template not found</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{template.title}</h1>
        <p className="text-gray-600 mt-2">
          {template.authority_name} - Version {template.version}
        </p>
        {template.description && (
          <p className="text-gray-700 mt-4">{template.description}</p>
        )}
      </div>

      {template.sections && template.sections.length > 0 ? (
        <div className="space-y-4">
          {template.sections.map((section) => (
            <Card key={section.id}>
              <CardHeader>
                <CardTitle>
                  {section.code} - {section.title}
                </CardTitle>
                <CardDescription>
                  {section.items_count || 0} items
                </CardDescription>
              </CardHeader>
              <CardContent>
                {section.items && section.items.length > 0 ? (
                  <div className="space-y-2">
                    {section.items.map((item) => (
                      <div
                        key={item.id}
                        className="p-3 border rounded-lg"
                      >
                        <div className="font-medium">{item.code}</div>
                        <div className="text-sm text-gray-600 mt-1">
                          {item.requirement_text}
                        </div>
                        {item.required_evidence_type && (
                          <div className="text-xs text-gray-500 mt-2">
                            Evidence: {item.required_evidence_type}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-gray-500 text-sm">No items in this section</div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">
          No sections found
        </div>
      )}
    </div>
  );
}
