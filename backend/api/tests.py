from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Project, Indicator, Evidence, Section, Standard


class DriveFolderLinkTests(TestCase):
    """Tests for Drive folder linking endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description'
        )
    
    def test_link_drive_folder_success(self):
        """Test successful Drive folder linking."""
        url = f'/api/projects/{self.project.id}/link-drive-folder/'
        data = {
            'drive_folder_id': '1AbC123XYZ',
            'drive_linked_email': 'test@example.com'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['drive_folder_id'], '1AbC123XYZ')
        self.assertEqual(response.data['evidence_storage_mode'], 'gdrive')
        self.assertIsNotNone(response.data['drive_linked_at'])
        self.assertEqual(response.data['drive_linked_email'], 'test@example.com')
        
        # Verify database
        project = Project.objects.get(id=self.project.id)
        self.assertEqual(project.drive_folder_id, '1AbC123XYZ')
        self.assertEqual(project.evidence_storage_mode, 'gdrive')
    
    def test_link_drive_folder_missing_folder_id(self):
        """Test linking fails when folder_id is missing."""
        url = f'/api/projects/{self.project.id}/link-drive-folder/'
        data = {'drive_linked_email': 'test@example.com'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_unlink_drive_folder_success(self):
        """Test successful Drive folder unlinking."""
        # First link a folder
        self.project.drive_folder_id = '1AbC123XYZ'
        self.project.evidence_storage_mode = 'gdrive'
        self.project.save()
        
        url = f'/api/projects/{self.project.id}/unlink-drive-folder/'
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['drive_folder_id'])
        self.assertEqual(response.data['evidence_storage_mode'], 'local')
        self.assertIsNone(response.data['drive_linked_at'])
        
        # Verify database
        project = Project.objects.get(id=self.project.id)
        self.assertIsNone(project.drive_folder_id)
        self.assertEqual(project.evidence_storage_mode, 'local')


class EvidenceMetadataTests(TestCase):
    """Tests for evidence metadata creation."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            drive_folder_id='1AbC123XYZ',
            evidence_storage_mode='gdrive'
        )
        self.section = Section.objects.create(
            project=self.project,
            name='Section A'
        )
        self.standard = Standard.objects.create(
            section=self.section,
            name='Standard 1'
        )
        self.indicator = Indicator.objects.create(
            project=self.project,
            section=self.section,
            standard=self.standard,
            requirement='Test requirement'
        )
    
    def test_create_evidence_metadata_success(self):
        """Test successful evidence metadata creation."""
        url = '/api/evidence/'
        data = {
            'project': self.project.id,
            'indicator': self.indicator.id,
            'storage': 'gdrive',
            'title': 'Test Evidence',
            'original_filename': 'test.pdf',
            'drive_file_id': '1XYZ789',
            'drive_web_view_link': 'https://drive.google.com/file/d/1XYZ789/view',
            'drive_mime_type': 'application/pdf'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['storage'], 'gdrive')
        self.assertEqual(response.data['drive_file_id'], '1XYZ789')
        self.assertEqual(response.data['original_filename'], 'test.pdf')
        
        # Verify database
        evidence = Evidence.objects.get(id=response.data['id'])
        self.assertEqual(evidence.storage, 'gdrive')
        self.assertEqual(evidence.drive_file_id, '1XYZ789')
        self.assertEqual(evidence.project, self.project)
    
    def test_get_project_evidence_list(self):
        """Test retrieving evidence list for a project."""
        # Create some evidence
        Evidence.objects.create(
            project=self.project,
            indicator=self.indicator,
            title='Evidence 1',
            storage='gdrive',
            drive_file_id='1ABC'
        )
        Evidence.objects.create(
            project=self.project,
            indicator=self.indicator,
            title='Evidence 2',
            storage='local'
        )
        
        url = f'/api/projects/{self.project.id}/evidence/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], 'Evidence 1')
        self.assertEqual(response.data[1]['title'], 'Evidence 2')

