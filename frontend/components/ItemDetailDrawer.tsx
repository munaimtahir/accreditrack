"use client";

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import apiClient from '@/lib/api';
import { ItemStatus, Evidence, Comment } from '@/lib/types';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface ItemDetailDrawerProps {
  itemStatus: ItemStatus;
  onClose: () => void;
  onUpdate: () => void;
}

export function ItemDetailDrawer({
  itemStatus,
  onClose,
  onUpdate,
}: ItemDetailDrawerProps) {
  const { isQAAdmin, isCoordinator } = useAuth();
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [comments, setComments] = useState<Comment[]>([]);
  const [status, setStatus] = useState(itemStatus.status);
  const [completionPercent, setCompletionPercent] = useState(itemStatus.completion_percent);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchEvidence();
    fetchComments();
  }, [itemStatus.id]);

  const fetchEvidence = async () => {
    try {
      const response = await apiClient.instance.get(`/item-status/${itemStatus.id}/evidence/`);
      setEvidence(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch evidence:', error);
    }
  };

  const fetchComments = async () => {
    try {
      const response = await apiClient.instance.get(`/item-status/${itemStatus.id}/comments/`);
      setComments(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch comments:', error);
    }
  };

  const handleStatusUpdate = async () => {
    setLoading(true);
    try {
      await apiClient.instance.patch(`/item-status/${itemStatus.id}/`, {
        status,
        completion_percent: completionPercent,
      });
      onUpdate();
      onClose();
    } catch (error) {
      console.error('Failed to update status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('item_status', itemStatus.id);

    try {
      await apiClient.instance.post(`/item-status/${itemStatus.id}/evidence/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      fetchEvidence();
    } catch (error) {
      console.error('Failed to upload evidence:', error);
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) return;

    try {
      await apiClient.instance.post(`/item-status/${itemStatus.id}/comments/`, {
        text: newComment,
        type: 'General',
        item_status: itemStatus.id,
      });
      setNewComment('');
      fetchComments();
    } catch (error) {
      console.error('Failed to add comment:', error);
    }
  };

  const canUpdateStatus = isQAAdmin || isCoordinator;
  const canVerify = isQAAdmin && status === 'Submitted';

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{itemStatus.proforma_item_code}</DialogTitle>
          <DialogDescription>{itemStatus.proforma_item_text}</DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Status Update */}
          {canUpdateStatus && (
            <div className="space-y-4">
              <div>
                <Label>Status</Label>
                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  className="w-full p-2 border rounded-md"
                  disabled={!canUpdateStatus}
                >
                  <option value="NotStarted">Not Started</option>
                  <option value="InProgress">In Progress</option>
                  <option value="Submitted">Submitted</option>
                  {isQAAdmin && (
                    <>
                      <option value="Verified">Verified</option>
                      <option value="Rejected">Rejected</option>
                    </>
                  )}
                </select>
              </div>
              <div>
                <Label>Completion Percentage</Label>
                <Input
                  type="number"
                  min="0"
                  max="100"
                  value={completionPercent}
                  onChange={(e) => setCompletionPercent(Number(e.target.value))}
                />
              </div>
              <Button onClick={handleStatusUpdate} disabled={loading}>
                Update Status
              </Button>
            </div>
          )}

          {/* Evidence */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Evidence</h3>
              {canUpdateStatus && (
                <label className="cursor-pointer">
                  <span className="text-sm text-blue-600 hover:underline">Upload File</span>
                  <input
                    type="file"
                    className="hidden"
                    onChange={handleFileUpload}
                    accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                  />
                </label>
              )}
            </div>
            <div className="space-y-2">
              {evidence.map((ev) => (
                <div key={ev.id} className="p-3 border rounded-lg">
                  <a
                    href={ev.file_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    {ev.file_name}
                  </a>
                  <div className="text-xs text-gray-500 mt-1">
                    Uploaded by {ev.uploaded_by_email} on{' '}
                    {new Date(ev.uploaded_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
              {evidence.length === 0 && (
                <div className="text-sm text-gray-500">No evidence uploaded</div>
              )}
            </div>
          </div>

          {/* Comments */}
          <div className="space-y-4">
            <h3 className="font-semibold">Comments</h3>
            <div className="space-y-2">
              {comments.map((comment) => (
                <div key={comment.id} className="p-3 border rounded-lg">
                  <div className="font-medium text-sm">{comment.author_name}</div>
                  <div className="text-sm text-gray-600 mt-1">{comment.text}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {new Date(comment.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
              {comments.length === 0 && (
                <div className="text-sm text-gray-500">No comments</div>
              )}
            </div>
            {canUpdateStatus && (
              <div className="flex gap-2">
                <Input
                  placeholder="Add a comment..."
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                />
                <Button onClick={handleAddComment}>Add</Button>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
