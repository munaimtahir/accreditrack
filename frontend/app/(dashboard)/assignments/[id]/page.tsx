"use client";

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import apiClient from '@/lib/api';
import { Assignment, ItemStatus } from '@/lib/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ItemDetailDrawer } from '@/components/ItemDetailDrawer';

interface SectionData {
  section: {
    id: string;
    code: string;
    title: string;
    weight: number;
  };
  items: ItemStatus[];
}

export default function AssignmentDetailPage() {
  const params = useParams();
  const { isQAAdmin, isCoordinator } = useAuth();
  const [assignment, setAssignment] = useState<Assignment | null>(null);
  const [sections, setSections] = useState<SectionData[]>([]);
  const [selectedItem, setSelectedItem] = useState<ItemStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.id) {
      fetchAssignment();
      fetchItems();
    }
  }, [params.id]);

  const fetchAssignment = async () => {
    try {
      const response = await apiClient.instance.get(`/assignments/${params.id}/`);
      setAssignment(response.data);
    } catch (error) {
      console.error('Failed to fetch assignment:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchItems = async () => {
    try {
      const response = await apiClient.instance.get(`/assignments/${params.id}/items/`);
      setSections(response.data);
    } catch (error) {
      console.error('Failed to fetch items:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Verified':
        return 'bg-green-100 text-green-800';
      case 'Submitted':
        return 'bg-blue-100 text-blue-800';
      case 'InProgress':
        return 'bg-yellow-100 text-yellow-800';
      case 'Rejected':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  if (!assignment) {
    return <div className="p-8">Assignment not found</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{assignment.proforma_template.title}</h1>
        <p className="text-gray-600 mt-2">
          {assignment.department.name} - Due: {new Date(assignment.due_date).toLocaleDateString()}
        </p>
        <div className="mt-4">
          <div className="text-sm text-gray-600">Overall Completion</div>
          <div className="text-3xl font-bold">{assignment.completion_percent}%</div>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div
              className="bg-blue-600 h-2 rounded-full"
              style={{ width: `${assignment.completion_percent}%` }}
            />
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {sections.map((sectionData) => {
          const sectionCompletion = sectionData.items.length > 0
            ? Math.round(
                (sectionData.items.filter((i) => i.status === 'Verified').length /
                  sectionData.items.length) *
                  100
              )
            : 0;

          return (
            <Card key={sectionData.section.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>
                      {sectionData.section.code} - {sectionData.section.title}
                    </CardTitle>
                    <CardDescription>
                      {sectionCompletion}% complete
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {sectionData.items.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                      onClick={() => setSelectedItem(item)}
                    >
                      <div className="flex-1">
                        <div className="font-medium">{item.proforma_item_code}</div>
                        <div className="text-sm text-gray-600 mt-1 line-clamp-1">
                          {item.proforma_item_text}
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}
                        >
                          {item.status}
                        </span>
                        <div className="text-sm text-gray-600">
                          {item.completion_percent}%
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {selectedItem && (
        <ItemDetailDrawer
          itemStatus={selectedItem}
          onClose={() => setSelectedItem(null)}
          onUpdate={fetchItems}
        />
      )}
    </div>
  );
}
