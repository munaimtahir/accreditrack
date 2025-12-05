"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import apiClient from '@/lib/api';
import { ProformaTemplate } from '@/lib/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

export default function ProformasPage() {
  const { isQAAdmin } = useAuth();
  const [templates, setTemplates] = useState<ProformaTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await apiClient.instance.get('/proformas/templates/', {
        params: { search, is_active: true },
      });
      setTemplates(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      fetchTemplates();
    }, 300);
    return () => clearTimeout(timeoutId);
  }, [search]);

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Proforma Templates</h1>
          <p className="text-gray-600 mt-2">View and manage accreditation templates</p>
        </div>
        {isQAAdmin && (
          <Button asChild>
            <Link href="/proformas/new">Create Template</Link>
          </Button>
        )}
      </div>

      <div className="flex gap-4">
        <Input
          placeholder="Search templates..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-sm"
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {templates.map((template) => (
          <Link key={template.id} href={`/proformas/${template.id}`}>
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <CardTitle>{template.title}</CardTitle>
                <CardDescription>
                  {template.authority_name} - v{template.version}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 line-clamp-2">
                  {template.description}
                </p>
                <div className="mt-4 text-sm text-gray-500">
                  {template.sections_count || 0} sections
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      {templates.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No templates found
        </div>
      )}
    </div>
  );
}
